CC ?= cc
CFLAGS ?= -Os -std=c11 -D_DEFAULT_SOURCE -Wall -Wextra -Werror
LDFLAGS ?=
TARGET := foldview_onvifd

.PHONY: all test clean
all: $(TARGET)

$(TARGET): src/foldview_onvifd.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

test: $(TARGET)
	python3 -m unittest discover -s tests -v

clean:
	rm -f $(TARGET)
