# Latest documentation and repository selection | 10 Nov 2026

Verified with Context7 (source documentation):

1. **OpenCV 4.13** `/websites/opencv`: `createBackgroundSubtractorMOG2`, frame foreground masks, contour thresholds. Runtime OpenCV 4.13 was available in local unit-test environment. Upstream license: Apache-2.0.
2. **FastALPR 0.4.0** `/ankandrew/fast-alpr`: `from fast_alpr import ALPR`, `ALPR(detector_model="yolo-v9-t-384-license-plate-end2end", ocr_model="cct-xs-v2-global-model")`, `.predict(frame)` with `result.detection.bounding_box`, `result.ocr.text`, `result.ocr.confidence`. Direct GitHub package files confirm source license MIT and Python >=3.10.
3. **FastAPI** `/websites/fastapi_tiangolo`: `APIKeyHeader` + FastAPI dependency. Our API compares a configured long secret using Python `secrets.compare_digest`. FastAPI version 0.122+ replies 401 for missing API key; testing verified that behavior on local FastAPI v0.128.2.
4. **Ultralytics YOLO** `/ultralytics/ultralytics`: validated current `YOLO(...).predict()` results API and model classification confidence. Deliberately **not included** in this proprietary project because official Ultralytics license notes the AGPL-3.0/Enterprise commercial dual licensing. Source implementation uses MIT-licensed FastALPR Python package instead, though model weight license must still be audited.
5. **OpenCV Zoo YuNet**: official MIT-licensed face detector model. Optional model path improves accuracy; bundled Haar fallback works without custom model downloads but is less robust.

## Starred repository verification

The user requested reuse of GitHub repositories they previously starred. The connected GitHub API does **not** permit user starred collection listing through its `fetch` interface, and public web retrieval of the stars tab was unsuccessful. Therefore **we cannot honestly assert which tools are in the user's starred list**. Candidate tools have been verified by their own upstream repositories and docs, but not as user-starred. This remains an explicit follow-up audit item and must not be silently relabeled.

## Model rights and privacy

The FastALPR framework is MIT, but third-party ONNX detector and OCR model weights have their own model-card terms; check before contracted procurement, redistribution or embedding. Do not copy pretrained weights into this GitHub repository. Local ONNX caches should be access-restricted and asset provenance recorded. For faces, stage 1 captures **sightings not identities** and performs no biometric embeddings, matching, or watchlists. All face/plate evidence is sensitive and should be processed only for authorized surveillance purposes with access controls, audit logging and deletion schedules aligned to the signed Garda project KAK/organizational policy. 

Upstream links:
- https://github.com/ankandrew/fast-alpr
- https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet
- https://github.com/opencv/opencv
- https://fastapi.tiangolo.com/reference/security/
- https://www.ultralytics.com/license
