/*
 * FOLDVIEW native ONVIF proof-of-concept for Fullhan FH8852V201.
 *
 * Independent protocol façade that reuses the stock RTSP streams.
 * No MTD writes, no PTZ, no firmware changes, no audio backchannel.
 * Prototype: read-only Device/Media operations only.
 *
 * WARNING: Discovery and metadata are intentionally LAN-visible; no ONVIF
 * WS-Security authentication is implemented. Do not deploy to an untrusted
 * segment or expose ports 3702/8899 outside a dedicated camera VLAN.
 * Do not claim production ONVIF Profile S compliance from this build.
 */
#define _POSIX_C_SOURCE 200809L
#include <arpa/inet.h>
#include <ctype.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

#define MAX_REQUEST 12288
#define MAX_RESPONSE 12288

struct config {
    char ip[INET_ADDRSTRLEN];
    int http_port;
    int main_rtsp;
    int sub_rtsp;
    char uuid[48];
};
static volatile sig_atomic_t running = 1;

static void on_signal(int sig) { (void)sig; running = 0; }
static void fail(const char *step) { perror(step); exit(1); }

static int write_all(int fd, const char *text, size_t len) {
    while (len > 0) {
        ssize_t n = send(fd, text, len, 0);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) return -1;
        text += n;
        len -= (size_t)n;
    }
    return 0;
}

static int new_http(int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) fail("tcp socket");
    int one = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));
    struct sockaddr_in bind_to;
    memset(&bind_to, 0, sizeof(bind_to));
    bind_to.sin_family = AF_INET;
    bind_to.sin_port = htons((unsigned short)port);
    bind_to.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(fd, (struct sockaddr *)&bind_to, sizeof(bind_to)) != 0) fail("http bind");
    if (listen(fd, 4) != 0) fail("http listen");
    return fd;
}

static int new_discovery(void) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) fail("udp socket");
    int one = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));
    struct sockaddr_in a;
    memset(&a, 0, sizeof(a));
    a.sin_family = AF_INET;
    a.sin_port = htons(3702);
    a.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(fd, (struct sockaddr *)&a, sizeof(a)) != 0) fail("udp 3702 bind");
    struct ip_mreq group;
    memset(&group, 0, sizeof(group));
    group.imr_multiaddr.s_addr = inet_addr("239.255.255.250");
    group.imr_interface.s_addr = htonl(INADDR_ANY);
    if (setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &group, sizeof(group)) != 0)
        fail("WS-Discovery multicast join");
    return fd;
}

static void discover_reply(int fd, const struct config *cfg) {
    char input[8192], output[8192], relates[200] = "urn:uuid:unknown";
    struct sockaddr_in sender;
    socklen_t sender_len = sizeof(sender);
    ssize_t n = recvfrom(fd, input, sizeof(input) - 1, 0,
                         (struct sockaddr *)&sender, &sender_len);
    if (n <= 0) return;
    input[n] = '\0';
    /* Do not answer arbitrary probes or expose an unauthenticated shell. */
    if (!strstr(input, "Probe") || !strstr(input, "discovery")) return;
    char *message = strstr(input, "MessageID>");
    if (message) {
        message += strlen("MessageID>");
        char *close = strchr(message, '<');
        if (close && close > message && (size_t)(close - message) < sizeof(relates)) {
            size_t len = (size_t)(close - message);
            int valid = 1;
            for (size_t i = 0; i < len; ++i) {
                unsigned char ch = (unsigned char)message[i];
                if (!isalnum(ch) && ch != ':' && ch != '-' && ch != '_' && ch != '.') {
                    valid = 0;
                    break;
                }
            }
            /* Never reflect untrusted XML into the WS-Discovery response. */
            if (valid) {
                memcpy(relates, message, len);
                relates[len] = '\0';
            }
        }
    }
    int size = snprintf(output, sizeof(output),
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        "<s:Envelope xmlns:s=\"http://www.w3.org/2003/05/soap-envelope\""
        " xmlns:a=\"http://schemas.xmlsoap.org/ws/2004/08/addressing\""
        " xmlns:d=\"http://schemas.xmlsoap.org/ws/2005/04/discovery\""
        " xmlns:dn=\"http://www.onvif.org/ver10/network/wsdl\">"
        "<s:Header><a:Action s:mustUnderstand=\"1\">"
        "http://schemas.xmlsoap.org/ws/2005/04/discovery/ProbeMatches</a:Action>"
        "<a:MessageID>urn:uuid:%s</a:MessageID>"
        "<a:RelatesTo>%s</a:RelatesTo>"
        "<a:To s:mustUnderstand=\"1\">"
        "http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous"
        "</a:To></s:Header><s:Body><d:ProbeMatches><d:ProbeMatch>"
        "<a:EndpointReference><a:Address>urn:uuid:%s</a:Address></a:EndpointReference>"
        "<d:Types>dn:NetworkVideoTransmitter</d:Types>"
        "<d:Scopes>onvif://www.onvif.org/type/video_encoder "
        "onvif://www.onvif.org/name/FOLDVIEW_FH8852V201</d:Scopes>"
        "<d:XAddrs>http://%s:%d/onvif/device_service</d:XAddrs>"
        "<d:MetadataVersion>1</d:MetadataVersion>"
        "</d:ProbeMatch></d:ProbeMatches></s:Body></s:Envelope>",
        cfg->uuid, relates, cfg->uuid, cfg->ip, cfg->http_port);
    if (size > 0 && size < (int)sizeof(output))
        sendto(fd, output, (size_t)size, 0, (struct sockaddr *)&sender, sender_len);
}

static int read_http(int fd, char *input, size_t cap) {
    size_t n = 0;
    int required = -1;
    while (n + 1 < cap) {
        ssize_t got = recv(fd, input + n, cap - 1 - n, 0);
        if (got < 0 && errno == EINTR) continue;
        if (got <= 0) break;
        n += (size_t)got;
        input[n] = '\0';
        char *end = strstr(input, "\r\n\r\n");
        if (!end) continue;
        size_t header_len = (size_t)(end - input) + 4;
        if (required < 0) {
            required = 0;
            char *p = input;
            while (p < end) {
                char *line_end = strstr(p, "\r\n");
                if (!line_end || line_end > end) break;
                if (strncasecmp(p, "Content-Length:", 15) == 0) {
                    const char *raw = p + 15;
                    while (raw < line_end && (*raw == ' ' || *raw == '\t')) ++raw;
                    if (raw >= line_end || !isdigit((unsigned char)*raw)) return -1;
                    errno = 0;
                    char *after = NULL;
                    long value = strtol(raw, &after, 10);
                    if (errno || after == raw || after > line_end ||
                        value < 0 || value > (long)(cap - header_len - 1)) return -1;
                    while (after < line_end && (*after == ' ' || *after == '\t')) ++after;
                    if (after != line_end) return -1;
                    required = (int)value;
                }
                p = line_end + 2;
            }
        }
        if (n >= header_len + (size_t)required) return (int)n;
    }
    return -1;
}

static int soap_body(const char *req, const struct config *cfg,
                     char *dst, size_t cap) {
    const char *dev = "http://www.onvif.org/ver10/device/wsdl";
    (void)dev;
    if (strstr(req, "GetDeviceInformation")) {
        return snprintf(dst, cap,
          "<tds:GetDeviceInformationResponse>"
          "<tds:Manufacturer>Fullhan</tds:Manufacturer>"
          "<tds:Model>FH8852V201 FOLDVIEW prototype</tds:Model>"
          "<tds:FirmwareVersion>stock-vendor-plus-volatile-onvifd</tds:FirmwareVersion>"
          "<tds:SerialNumber>not-exported</tds:SerialNumber>"
          "<tds:HardwareId>FH8852V201</tds:HardwareId>"
          "</tds:GetDeviceInformationResponse>");
    }
    if (strstr(req, "GetSystemDateAndTime")) {
        return snprintf(dst, cap,
          "<tds:GetSystemDateAndTimeResponse><tds:SystemDateAndTime>"
          "<tt:DateTimeType>Manual</tt:DateTimeType><tt:DaylightSavings>false"
          "</tt:DaylightSavings></tds:SystemDateAndTime>"
          "</tds:GetSystemDateAndTimeResponse>");
    }
    if (strstr(req, "GetCapabilities")) {
        return snprintf(dst, cap,
          "<tds:GetCapabilitiesResponse><tds:Capabilities>"
          "<tt:Device><tt:XAddr>http://%s:%d/onvif/device_service</tt:XAddr>"
          "</tt:Device>"
          "<tt:Media><tt:XAddr>http://%s:%d/onvif/media_service</tt:XAddr>"
          "<tt:StreamingCapabilities>"
          "<tt:RTPMulticast>false</tt:RTPMulticast>"
          "<tt:RTP_TCP>true</tt:RTP_TCP>"
          "<tt:RTP_RTSP_TCP>true</tt:RTP_RTSP_TCP>"
          "</tt:StreamingCapabilities></tt:Media>"
          "</tds:Capabilities></tds:GetCapabilitiesResponse>",
          cfg->ip, cfg->http_port, cfg->ip, cfg->http_port);
    }
    if (strstr(req, "GetServices")) {
        return snprintf(dst, cap,
          "<tds:GetServicesResponse>"
          "<tds:Service><tds:Namespace>http://www.onvif.org/ver10/device/wsdl"
          "</tds:Namespace><tds:XAddr>http://%s:%d/onvif/device_service</tds:XAddr>"
          "<tds:Version><tt:Major>2</tt:Major><tt:Minor>0</tt:Minor>"
          "</tds:Version></tds:Service>"
          "<tds:Service><tds:Namespace>http://www.onvif.org/ver10/media/wsdl"
          "</tds:Namespace><tds:XAddr>http://%s:%d/onvif/media_service</tds:XAddr>"
          "<tds:Version><tt:Major>2</tt:Major><tt:Minor>0</tt:Minor>"
          "</tds:Version></tds:Service>"
          "</tds:GetServicesResponse>",
          cfg->ip, cfg->http_port, cfg->ip, cfg->http_port);
    }
    if (strstr(req, "GetScopes")) {
        return snprintf(dst, cap,
          "<tds:GetScopesResponse><tds:Scopes>"
          "<tt:ScopeDef>Fixed</tt:ScopeDef>"
          "<tt:ScopeItem>onvif://www.onvif.org/type/video_encoder</tt:ScopeItem>"
          "</tds:Scopes></tds:GetScopesResponse>");
    }
    if (strstr(req, "GetProfiles") || strstr(req, "GetProfile")) {
        return snprintf(dst, cap,
          "<trt:GetProfilesResponse>"
          "<trt:Profiles token=\"Profile_Main\" fixed=\"true\">"
          "<tt:Name>Main 1080p</tt:Name>"
          "<tt:VideoSourceConfiguration token=\"VSC_Main\">"
          "<tt:Name>Camera source</tt:Name><tt:UseCount>1</tt:UseCount>"
          "<tt:SourceToken>VS_1</tt:SourceToken>"
          "<tt:Bounds x=\"0\" y=\"0\" width=\"1920\" height=\"1080\"/>"
          "</tt:VideoSourceConfiguration>"
          "</trt:Profiles>"
          "<trt:Profiles token=\"Profile_Sub\" fixed=\"true\">"
          "<tt:Name>Sub</tt:Name>"
          "</trt:Profiles>"
          "</trt:GetProfilesResponse>");
    }
    if (strstr(req, "GetStreamUri")) {
        int port = strstr(req, "Profile_Sub") ? cfg->sub_rtsp : cfg->main_rtsp;
        return snprintf(dst, cap,
          "<trt:GetStreamUriResponse><trt:MediaUri>"
          "<tt:Uri>rtsp://%s:%d/</tt:Uri>"
          "<tt:InvalidAfterConnect>false</tt:InvalidAfterConnect>"
          "<tt:InvalidAfterReboot>false</tt:InvalidAfterReboot>"
          "<tt:Timeout>PT0S</tt:Timeout>"
          "</trt:MediaUri></trt:GetStreamUriResponse>", cfg->ip, port);
    }
    return snprintf(dst, cap,
        "<s:Fault><s:Code><s:Value>s:Sender</s:Value>"
        "<s:Subcode><s:Value>ter:ActionNotSupported</s:Value>"
        "</s:Subcode></s:Code><s:Reason>"
        "<s:Text xml:lang=\"en\">Operation not implemented</s:Text>"
        "</s:Reason></s:Fault>");
}

static void serve_http(int fd, const struct config *cfg) {
    char input[MAX_REQUEST], body[5500], response[MAX_RESPONSE];
    struct timeval timeout = {3, 0};
    if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) != 0 ||
        setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout)) != 0) return;
    if (read_http(fd, input, sizeof(input)) < 0) return;
    if (strncmp(input, "POST /onvif/", 12) != 0) {
        const char *s = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n"
                        "Connection: close\r\n\r\n";
        write_all(fd, s, strlen(s));
        return;
    }
    int body_size = soap_body(input, cfg, body, sizeof(body));
    if (body_size <= 0 || body_size >= (int)sizeof(body)) return;
    int total = snprintf(response, sizeof(response),
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        "<s:Envelope xmlns:s=\"http://www.w3.org/2003/05/soap-envelope\""
        " xmlns:tds=\"http://www.onvif.org/ver10/device/wsdl\""
        " xmlns:trt=\"http://www.onvif.org/ver10/media/wsdl\""
        " xmlns:tt=\"http://www.onvif.org/ver10/schema\""
        " xmlns:ter=\"http://www.onvif.org/ver10/error\">"
        "<s:Body>%s</s:Body></s:Envelope>", body);
    if (total < 0 || total >= (int)sizeof(response)) return;
    char header[250];
    int length = snprintf(header, sizeof(header),
        "HTTP/1.1 200 OK\r\nContent-Type: application/soap+xml; charset=utf-8\r\n"
        "Content-Length: %d\r\nConnection: close\r\n\r\n", total);
    if (length > 0 && length < (int)sizeof(header)) {
        if (write_all(fd, header, (size_t)length) == 0)
            write_all(fd, response, (size_t)total);
    }
}

static int port_arg(const char *text) {
    char *end = NULL;
    long port = strtol(text, &end, 10);
    if (!text[0] || *end != '\0' || port < 1024 || port > 65535) return -1;
    return (int)port;
}

int main(int argc, char **argv) {
    struct config cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.http_port = 8899;
    cfg.main_rtsp = 1234;
    cfg.sub_rtsp = 1235;
    strcpy(cfg.uuid, "e7201200-8150-4a03-a975-f8852f020100");
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--ip") && i + 1 < argc) {
            strncpy(cfg.ip, argv[++i], sizeof(cfg.ip) - 1);
        } else if (!strcmp(argv[i], "--http-port") && i + 1 < argc) {
            cfg.http_port = port_arg(argv[++i]);
        } else if (!strcmp(argv[i], "--main-port") && i + 1 < argc) {
            cfg.main_rtsp = port_arg(argv[++i]);
        } else if (!strcmp(argv[i], "--sub-port") && i + 1 < argc) {
            cfg.sub_rtsp = port_arg(argv[++i]);
        } else {
            fprintf(stderr, "usage: %s --ip <camera-lan-ip> "
                            "[--http-port 8899] [--main-port 1234] [--sub-port 1235]\n", argv[0]);
            return 2;
        }
    }
    struct in_addr ip;
    if (inet_pton(AF_INET, cfg.ip, &ip) != 1 || cfg.http_port < 0 ||
        cfg.main_rtsp < 0 || cfg.sub_rtsp < 0) {
        fprintf(stderr, "invalid options; provide explicit IPv4 and ports\n");
        return 2;
    }
    signal(SIGINT, on_signal);
    signal(SIGTERM, on_signal);
    signal(SIGPIPE, SIG_IGN);
    int udp = new_discovery();
    int http = new_http(cfg.http_port);
    fprintf(stderr, "FOLDVIEW experimental ONVIF: %s:%d, RTSP %d/%d (no PTZ)\n",
            cfg.ip, cfg.http_port, cfg.main_rtsp, cfg.sub_rtsp);
    while (running) {
        fd_set ready;
        FD_ZERO(&ready);
        FD_SET(udp, &ready);
        FD_SET(http, &ready);
        struct timeval timeout = {1, 0};
        int rc = select((udp > http ? udp : http) + 1, &ready, NULL, NULL, &timeout);
        if (rc < 0 && errno == EINTR) continue;
        if (rc < 0) break;
        if (FD_ISSET(udp, &ready)) discover_reply(udp, &cfg);
        if (FD_ISSET(http, &ready)) {
            int fd = accept(http, NULL, NULL);
            if (fd >= 0) { serve_http(fd, &cfg); close(fd); }
        }
    }
    close(http);
    close(udp);
    return 0;
}
