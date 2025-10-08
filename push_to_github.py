#!/usr/bin/env python3
"""
Script đẩy code lên GitHub
Hỗ trợ PyCharm, VS Code và Google Colab
"""

import subprocess
import sys
import os
from datetime import datetime

# Thêm GitHub CLI vào PATH cho môi trường ảo trên Windows
if sys.platform == "win32":
    github_cli_paths = [
        r"C:\Program Files\GitHub CLI",
        r"C:\Program Files (x86)\GitHub CLI",
        os.path.expanduser(r"~\AppData\Local\Programs\GitHub CLI")
    ]
    for cli_path in github_cli_paths:
        if os.path.exists(cli_path) and cli_path not in os.environ["PATH"]:
            os.environ["PATH"] = cli_path + ";" + os.environ["PATH"]


# Kiểm tra môi trường
def is_colab():
    """Kiểm tra có đang chạy trên Google Colab không"""
    try:
        import google.colab
        return True
    except ImportError:
        return False


def is_vscode():
    """Kiểm tra có đang chạy trên VS Code không"""
    return "VSCODE_PID" in os.environ


def run_command(command, description, capture=True, check_error=True):
    """Chạy command và hiển thị kết quả"""
    print(f"\n📌 {description}...")
    try:
        if capture:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            output = result.stdout.strip()
            if output:
                print(output)
            return output
        else:
            result = subprocess.run(command, shell=True, check=True)
            return "SUCCESS"
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if capture else str(e)
        if check_error:
            print(f"❌ Lỗi: {error_msg}")
            return None
        else:
            return error_msg.strip() if capture else str(e)


def get_input(prompt, default=None):
    """Lấy input từ user với giá trị mặc định"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def detect_ide():
    """Phát hiện môi trường IDE"""
    if is_colab():
        return "Google Colab"
    elif is_vscode():
        return "VS Code"
    elif "PYCHARM" in os.environ:
        return "PyCharm"
    else:
        return "Terminal/Local"


def setup_git_config():
    """Cấu hình Git nếu chưa được thiết lập"""
    print("\n🔧 Kiểm tra cấu hình Git...")

    # Kiểm tra user.name
    user_name = run_command("git config user.name", "Kiểm tra Git username", check_error=False)
    if not user_name:
        print("\n⚠️  Chưa cấu hình Git username")
        name = get_input("Nhập tên của bạn (cho Git config)", "Git User")
        run_command(f'git config --global user.name "{name}"', "Cấu hình username")

    # Kiểm tra user.email
    user_email = run_command("git config user.email", "Kiểm tra Git email", check_error=False)
    if not user_email:
        print("\n⚠️  Chưa cấu hình Git email")
        email = get_input("Nhập email (cho Git config)", "user@example.com")
        run_command(f'git config --global user.email "{email}"', "Cấu hình email")


def check_git_auth():
    """Kiểm tra và hướng dẫn authentication nếu cần"""
    remote_url = run_command(
        "git config --get remote.origin.url",
        "Lấy remote URL",
        check_error=False
    )

    if remote_url:
        print(f"📍 Remote URL: {remote_url}")

    if remote_url and "https://" in remote_url:
        print("\n🔐 Remote sử dụng HTTPS - có thể cần credentials")
        print("💡 Mẹo:")
        print("   1. Sử dụng Personal Access Token thay vì password")
        print("   2. Hoặc chuyển sang SSH: git remote set-url origin git@github.com:user/repo.git")


def get_current_branch():
    """Lấy branch hiện tại"""
    try:
        result = subprocess.run(
            "git branch --show-current",
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        current_branch = result.stdout.strip()
        return current_branch if current_branch else None
    except subprocess.CalledProcessError:
        return None


def main():
    print("=" * 60)
    print("🚀 PUSH CODE LÊN GITHUB")
    print("=" * 60)

    # Phát hiện môi trường
    ide = detect_ide()
    print(f"💻 Môi trường: {ide}")

    # Cấu hình Git nếu cần
    setup_git_config()
    check_git_auth()

    # Kiểm tra Git repository
    git_check = run_command("git rev-parse --git-dir", "Kiểm tra Git repository", check_error=False)
    if not git_check:
        print("❌ Không phải Git repository")
        print("💡 Hãy chắc chắn bạn đang trong thư mục Git repository")
        sys.exit(1)

    # Lấy branch hiện tại
    current_branch = get_current_branch()
    if not current_branch:
        print("❌ Không thể xác định branch hiện tại")
        sys.exit(1)

    print(f"📍 Branch hiện tại: {current_branch}")

    # Kiểm tra remote
    remote_check = run_command("git remote -v", "Kiểm tra remote", check_error=False)
    if not remote_check:
        print("\n❌ Chưa có remote repository")
        add_remote = get_input("Thêm remote ngay? (y/n)", "y").lower()
        if add_remote == 'y':
            remote_url = get_input("Nhập URL remote repository (GitHub)")
            run_command(f"git remote add origin {remote_url}", "Thêm remote")
        else:
            print("❌ Cần có remote để push code")
            sys.exit(1)

    # Kiểm tra có thay đổi không
    status = run_command("git status --porcelain", "Kiểm tra thay đổi", check_error=False)
    has_changes = bool(status and status.strip())

    if not has_changes:
        print("\n⚠️  Không có thay đổi nào để commit")

        # Kiểm tra có commit chưa push không
        unpushed = run_command(
            f"git log origin/{current_branch}..HEAD --oneline",
            "Kiểm tra commits chưa push",
            check_error=False
        )

        if unpushed and unpushed.strip():
            print(f"\n📝 Có {len(unpushed.strip().split(chr(10)))} commit(s) chưa push:")
            print(unpushed)
            push_only = get_input("Push các commits này? (y/n)", "y").lower()
        else:
            print("ℹ️  Không có commits mới để push")
            push_only = get_input("Vẫn muốn thử push? (y/n)", "n").lower()

        if push_only != 'y':
            print("✅ Không có gì để push")
            sys.exit(0)
    else:
        print("\n📝 Các file thay đổi:")
        status_lines = status.strip().split('\n') if status else []

        # Hiển thị tối đa 15 files
        for line in status_lines[:15]:
            print(f"   {line}")

        if len(status_lines) > 15:
            print(f"   ... và {len(status_lines) - 15} file(s) khác")

        # Xem chi tiết thay đổi nếu muốn
        review = get_input("\nXem chi tiết thay đổi? (y/n)", "n").lower()
        if review == 'y':
            run_command("git diff --stat", "Thống kê thay đổi", capture=False, check_error=False)

        # Add files
        add_all = get_input("\nThêm tất cả các thay đổi? (y/n)", "y").lower()

        if add_all == 'y':
            result = run_command("git add .", "Thêm tất cả các thay đổi")
            if result is None:
                print("❌ Lỗi khi thêm files")
                sys.exit(1)
        else:
            files_to_add = get_input("Nhập files cần add (cách nhau bởi dấu cách)")
            if files_to_add:
                result = run_command(f"git add {files_to_add}", "Thêm files đã chọn")
                if result is None:
                    print("❌ Lỗi khi thêm files")
                    sys.exit(1)
            else:
                print("❌ Không có files nào được chọn")
                sys.exit(1)

        # Commit
        print("\n💬 Mẫu commit message:")
        print("   - feat: thêm tính năng mới")
        print("   - fix: sửa lỗi")
        print("   - docs: cập nhật tài liệu")
        print("   - refactor: tái cấu trúc code")
        print("   - style: sửa định dạng")
        print("   - test: thêm tests")

        commit_msg = get_input("\nNhập commit message")
        if not commit_msg:
            print("❌ Commit message không được để trống")
            sys.exit(1)

        # Thêm prefix với tên
        add_author = get_input("Thêm tên vào commit? (y/n)", "n").lower()
        if add_author == 'y':
            author_name = get_input("Tên của bạn (VD: member1)")
            if author_name:
                commit_msg = f"[{author_name}] {commit_msg}"
            else:
                print("⚠️  Không có tên được thêm vào, sử dụng commit message gốc")

        # Commit thay đổi
        print(f"\n💾 Đang commit...")
        try:
            result = subprocess.run(
                f'git commit -m "{commit_msg}"',
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ Commit thành công!")
            if result.stdout:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Lỗi khi commit: {e.stderr}")
            sys.exit(1)

    # Pull trước khi push để tránh conflict
    print(f"\n🔄 Đồng bộ với remote...")
    pull_result = run_command(
        f"git pull origin {current_branch}",
        "Pull từ remote",
        check_error=False
    )

    if pull_result and "conflict" in pull_result.lower():
        print("\n⚠️  Có conflict! Cần giải quyết conflict trước khi push")
        print("   Chạy: git status để xem files conflict")
        print("   Sau khi giải quyết: git add . && git commit -m 'Resolve conflicts'")
        sys.exit(1)

    # PUSH
    print(f"\n🚀 Đang push branch '{current_branch}' lên GitHub...")

    # Kiểm tra branch đã có trên remote chưa
    try:
        remote_check = subprocess.run(
            f"git ls-remote --heads origin {current_branch}",
            shell=True,
            capture_output=True,
            text=True
        )
        remote_exists = bool(remote_check.stdout.strip())
    except:
        remote_exists = False

    if remote_exists:
        push_cmd = f"git push origin {current_branch}"
    else:
        push_cmd = f"git push -u origin {current_branch}"
        print(f"ℹ️  Branch mới, sẽ tạo trên remote")

    # Thực hiện push
    try:
        result = subprocess.run(push_cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ Push thành công!")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi push: {e.stderr}")

        # Phân tích lỗi chi tiết
        if "Permission denied" in e.stderr:
            print("\n🔐 Lỗi quyền truy cập:")
            print("   - Kiểm tra token/username/password")
            print("   - Đảm bảo bạn có quyền push vào repository này")
        elif "could not read Username" in e.stderr:
            print("\n🔐 Lỗi authentication:")
            print("   - Đối với HTTPS: sử dụng Personal Access Token thay vì password")
            print("   - Hoặc chuyển sang SSH: git remote set-url origin git@github.com:user/repo.git")
        elif "failed to push some refs" in e.stderr:
            print("\n🔄 Có thể cần pull trước:")
            print(f"   - Chạy: git pull origin {current_branch} --rebase")
            print("   - Sau đó chạy lại script")
        elif "non-fast-forward" in e.stderr:
            print("\n🔄 Remote có thay đổi mới:")
            print(f"   - Chạy: git pull origin {current_branch}")
            print("   - Giải quyết conflict nếu có")
            print("   - Sau đó chạy lại script")

        sys.exit(1)

    # Hiển thị kết quả cuối cùng
    print("\n" + "=" * 60)
    print("✅ HOÀN TẤT!")
    print("=" * 60)
    print(f"📍 Branch: {current_branch}")
    print("✅ Code đã được push lên GitHub thành công!")

    # Hiển thị commit cuối
    print("\n📝 Commit vừa push:")
    run_command("git log -1 --oneline", "Hiển thị commit", check_error=False)

    # Hiển thị trạng thái remote
    remote_url = run_command("git config --get remote.origin.url", "Lấy remote URL", check_error=False)
    if remote_url and "github.com" in remote_url:
        if remote_url.startswith("git@github.com:"):
            repo_path = remote_url.replace("git@github.com:", "").replace(".git", "")
        elif "https://github.com/" in remote_url:
            repo_path = remote_url.replace("https://github.com/", "").replace(".git", "")
        else:
            repo_path = None

        if repo_path:
            print(f"\n🌐 Kiểm tra trên GitHub:")
            print(f"   🔗 Repository: https://github.com/{repo_path}")
            print(f"   🔗 Branch: https://github.com/{repo_path}/tree/{current_branch}")

    print("\n🎉 Chúc mừng! Code đã được đẩy lên GitHub!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy bỏ")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        sys.exit(1)