"""Every test named in spec/features/*.feature must exist. Exit 1 if any is missing."""
import glob, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
names = set(re.findall(r"def (test_\w+)", "".join(Path(f).read_text() for f in glob.glob(str(ROOT / "tests" / "*.py")))))
missing = []
for f in sorted(glob.glob(str(ROOT / "spec" / "features" / "*.feature"))):
    for line in Path(f).read_text().splitlines():
        if "#" in line:
            for r in re.findall(r"(test_\w+)", line.split("#", 1)[1]):
                if r not in names:
                    missing.append((Path(f).name, r))
print("spec->test links:", "OK" if not missing else missing)
sys.exit(1 if missing else 0)
