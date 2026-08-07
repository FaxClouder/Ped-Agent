# Vision trajectory workbench

Ped-Agent's local single-user vision path is:

`upload -> preflight -> single GPU queue -> detection/tracking -> review -> calibration -> projection -> postprocess -> analysis -> rendering/export`

The authoritative runtime directory is `Video-Analysis/runtime/` and is Git-ignored. SQLite
stores task state, events, review patches and artifact indexes only. Frame-level trajectory data
is stored as Parquet; scene profiles, calibration reports, analysis bundles and provenance use
JSON/GeoJSON-compatible objects.

## Runtime installation

```powershell
uv sync --project backend --extra vision --group dev
uv run --project backend ped-agent serve
```

The visual worker is a single queue. CUDA uses FP16 by default; CPU uses FP32. Missing optional
CV dependencies cause the affected task to enter `failed` with a retry checkpoint, without
damaging completed artifacts.

## Model manifest boundary

Place detector YAML under `Video-Analysis/src/ped_video_analysis/configs/detectors/` and its
custom Ultralytics-compatible weights under `Video-Analysis/models/weights/`. Relative weight
paths resolve against the module weight directory. The server verifies the weight SHA-256 before
accepting a task.

```json
{
  "model_id": "mixed-flow-v1",
  "name": "Mixed flow detector and contact keypoints",
  "version": "1.0.0",
  "backend": "ultralytics",
  "weights_path": "mixed-flow-v1.pt",
  "sha256": "REPLACE_WITH_64_HEX_WEIGHT_DIGEST",
  "input_size": 1280,
  "class_map": {
    "0": "pedestrian",
    "1": "pedestrian_umbrella",
    "2": "bicycle_rider",
    "3": "ebike_rider"
  },
  "keypoint_names": ["left_foot", "right_foot", "front_wheel", "rear_wheel"],
  "contact_keypoints": {
    "pedestrian": ["left_foot", "right_foot"],
    "pedestrian_umbrella": ["left_foot", "right_foot"],
    "bicycle_rider": ["front_wheel", "rear_wheel"],
    "ebike_rider": ["front_wheel", "rear_wheel"]
  }
}
```

The four classes are mutually exclusive. Pedestrian classes and rider classes are separate
association groups. The final class is the confidence-weighted trajectory vote. Missing contact
keypoints fall back to a degraded point and enter the review queue.

## Calibration gate

Two paths are supported:

- Full camera: import camera intrinsics/distortion, use the ChArUco helper when needed, then solve
  ground-plane extrinsics from distributed control points.
- Homography compatibility: at least eight fit points, normalized DLT, RANSAC and nonlinear
  refinement.

Fit points and independent checkpoints are separate. At least four checkpoints are required.
World-coordinate RMSE must be at most `0.10 m`; otherwise pixel tracks remain available but
speed, density, TTC, PET and other formal metre-based outputs are withheld.

## Immutable artifacts and recomputation

The task state flow is:

`uploaded -> preflighted -> queued -> inference_running -> awaiting_review -> awaiting_calibration -> projection_running -> postprocess_running -> analysis_running -> rendering -> completed`

`failed` and `cancelled` retain `resume_status`. Retry resumes that stage. Review or calibration
revisions deactivate only the affected downstream indexes; the old files remain for provenance.
Changing calibration never reruns detection/tracking.

## API resources

- `GET /api/vision/models`
- `GET|POST /api/vision/scenes`
- `POST /api/vision/scenes/from-pixel-geometry`
- `POST /api/vision/scenes/calibrate/charuco`
- `POST /api/vision/scenes/{id}/calibrate/homography`
- `GET|POST /api/vision/tasks`
- `GET /api/vision/tasks/{id}/events`
- `POST /api/vision/tasks/{id}/review`
- `POST /api/vision/tasks/{id}/calibration`
- `POST /api/vision/tasks/{id}/rerun`
- `POST /api/vision/tasks/{id}/cancel`
- `GET /api/vision/tasks/{id}/results`
- `GET /api/vision/tasks/{id}/exports`

The Agent consumes results read-only. It does not automatically create or rerun visual tasks.

The workbench keeps video-drawn geometry in pixel coordinates until a calibration report is
selected. The server applies the accepted homography or full-camera ground-plane projection and
only then writes a new immutable, metre-based `SceneProfile` version. Review patches can batch
delete, relabel, split, merge and contact-point correction operations.

## Outputs

Exports contain CSV, JSON, Parquet, Plotly JSON, SVG, PDF, 300 DPI PNG and a provenance manifest.
Figures include units, sample count, scene/calibration lineage and analysis parameters. Interaction
outputs are proxy metrics only and never a safety or compliance conclusion. No output video is
created anywhere in the result tree.

When PedPy is installed and the scene geometry is supported, classic density, speed fields,
speed profiles, fundamental diagrams and Voronoi density use PedPy 1.5-compatible APIs. The
analysis bundle records the selected method. Missing PedPy, unsupported measurement geometry or
degenerate duplicate positions fall back to the local bounded implementation without fabricating
zero physical metrics.
