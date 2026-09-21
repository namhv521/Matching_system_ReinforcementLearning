"""Installer and environment verification script for KLTN AI Agent."""

import sys
import subprocess
import os
from pathlib import Path

REQUIRED_PACKAGES = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic-settings",
    "pytest",
]

OPTIONAL_PACKAGES = [
    "langgraph",
    "langchain-core",
    "openai",
    "ragas",
]


def check_python_version():
    """Verify minimum Python 3.10 requirement."""
    print("🔍 Kiểm tra phiên bản Python...")
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        print(f"❌ Yêu cầu Python >= 3.10. Phiên bản hiện tại: {v.major}.{v.minor}.{v.micro}")
        sys.exit(1)
    print(f"✅ Python {v.major}.{v.minor}.{v.micro} hợp lệ.")


def check_and_install_dependencies():
    """Check required dependencies and offer installation if missing."""
    print("\n📦 Kiểm tra thư viện bắt buộc:")
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg.replace("-", "_"))
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg} (chưa cài)")
            missing.append(pkg)

    if missing:
        print(f"\n⚙️ Đang cài đặt các thư viện còn thiếu: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        print("✅ Hoàn thành cài đặt thư viện bắt buộc!")
    else:
        print("✅ Toàn bộ thư viện bắt buộc đã sẵn sàng.")


def prepare_directories():
    """Ensure runtime folders exist."""
    print("\n📁 Khởi tạo cấu trúc thư mục lưu trữ...")
    base_dir = Path(__file__).resolve().parents[1]
    dirs = [
        base_dir / "logs" / "agent",
        base_dir / "eval",
        base_dir / "data" / "storage",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  📁 {d.relative_to(base_dir)}")
    print("✅ Cấu trúc thư mục sẵn sàng.")


def main():
    print("=" * 60)
    print("🚀 BẮT ĐẦU THIẾT LẬP KLTN AI AGENT")
    print("=" * 60)
    check_python_version()
    check_and_install_dependencies()
    prepare_directories()
    print("\n🎉 Hoàn tất thiết lập! Bạn có thể chạy Agent bằng:")
    print("   python -m uvicorn src.main:app --reload --port 8000")
    print("=" * 60)


if __name__ == "__main__":
    main()
