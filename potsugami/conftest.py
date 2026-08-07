import sys
from pathlib import Path

# インストールなしで src レイアウトのパッケージをテストできるようにする
sys.path.insert(0, str(Path(__file__).parent / "src"))
