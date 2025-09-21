"""Convert raw scan counts into coarse calibration metrics and quick plots."""

import numpy as np


def calibrate(y, z, n_beam, n_left, n_right, n_triggered=None, logic="or"):
    """Return rough midline, gain, and per-point efficiencies from scan data."""

    arr = lambda a: np.asarray(a, float)  # convert everything to float arrays
    y, z, n_beam = map(arr, (y, z, n_beam))
    n_left, n_right = map(arr, (n_left, n_right))
    trig = arr(n_triggered) if n_triggered is not None else (
        np.maximum(n_left, n_right) if logic == "or" else np.minimum(n_left, n_right)
    )  # default triggered counts from OR/AND if none supplied

# maybe not needed
    p_left = np.divide(n_left, n_beam, out=np.full_like(n_left, np.nan), where=n_beam > 0)  # efficiency left cube
    p_right = np.divide(n_right, n_beam, out=np.full_like(n_right, np.nan), where=n_beam > 0)  # efficiency right cube
    p_logic = np.divide(trig, n_beam, out=np.full_like(trig, np.nan), where=n_beam > 0)  # chosen trigger efficiency
    asym = (p_right - p_left) / (p_right + p_left)  # simple asymmetry signal

    def _midline(axis, mask):
        axis = axis[mask]  # subset to the sweep we care about
        p = p_logic[mask]
        if not axis.size:
            return 0.0
        return float(axis[np.nanargmax(p)])  # pick the position with highest efficiency

    TOL = 2.0  # stage moves in 2 mm steps; treat that as our neighbourhood
    y0 = _midline(y, np.isclose(z, np.median(z), atol=TOL))
    z0 = _midline(z, np.isclose(y, np.median(y), atol=TOL))

    gain = 1.0  # gain balancing handled elsewhere when mapping sensors

    score = np.nan_to_num(p_logic, nan=-1)
    best = int(np.argmax(score))

    centre_mask = np.isclose(y, y0, atol=TOL) & np.isclose(z, z0, atol=TOL)  # repeated hits near centre
    drift = (
        float(p_logic[centre_mask][-1] - p_logic[centre_mask][0])
        if np.count_nonzero(centre_mask) > 1
        else np.nan
    )

    return {
        "y0": y0,
        "z0": z0,
        "gain": gain,
        "operating_point": (float(y[best]), float(z[best]), float(p_logic[best])),
        "metrics": {"p_left": p_left, "p_right": p_right, "p_logic": p_logic, "asym": asym},
        "center_drift": drift,
    }


def plot_calibration_face(y, z, y0, z0, ax=None):
    """Plot scan locations on the detector face, highlighting the raster grid."""

    import matplotlib.pyplot as plt

    y = np.asarray(y, float)
    z = np.asarray(z, float)
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
    for yy, zz in zip(y, z):
        color = "green" if abs(yy - y0) <= 2 and abs(zz - z0) <= 2 and (yy != y0 or zz != z0) else "black"
        size = 70 if color == "green" else 40
        ax.scatter(yy, zz, color=color, s=size)
    ax.scatter([y0], [z0], color="red", s=160, label="(y0, z0)")
    ax.text(y0 + 1.5, z0 + 1.5, "(y0, z0)", color="red", fontsize=9)
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("z (mm)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle="--", alpha=0.4)
    span = max(np.max(np.abs(y)), np.max(np.abs(z))) if y.size else 1
    pad = max(2.0, span * 1.1)
    ax.set_xlim(-pad, pad)
    ax.set_ylim(-pad, pad)
    ax.axhline(0.0, color="blue", linestyle="--", linewidth=1, label="z = 0")
    ax.axvline(y0, color="purple", linestyle="--", linewidth=1, label="y = y0")
    ax.legend(loc="upper right")
    ax.set_title("Calibration Points on Detector Face")
    return ax


if __name__ == "__main__":
    import csv
    import sys

    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/calibration_numpy.py calibration.csv")

    path = sys.argv[1]
    with open(path, "r", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    required = ["y_mm", "z_mm", "n_beam", "n_left", "n_right"]
    missing = [col for col in required if col not in reader.fieldnames]
    if missing:
        sys.exit(f"missing columns: {missing}")

    y = [float(r["y_mm"]) for r in rows]
    z = [float(r["z_mm"]) for r in rows]
    n_beam = [float(r["n_beam"]) for r in rows]
    n_left = [float(r["n_left"]) for r in rows]
    n_right = [float(r["n_right"]) for r in rows]
    n_triggered = [float(r["n_triggered"]) for r in rows] if "n_triggered" in reader.fieldnames else None

    result = calibrate(y, z, n_beam, n_left, n_right, n_triggered=n_triggered)

    print("y0_mm:", result["y0"])
    print("z0_mm:", result["z0"])
    print("gain_scalar:", result["gain"])
    y_best, z_best, eff_best = result["operating_point"]
    print("operating_point:", (y_best, z_best), "efficiency:", eff_best)
    print("center_drift:", result["center_drift"])
