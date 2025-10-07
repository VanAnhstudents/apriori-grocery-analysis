#!/usr/bin/env python3
"""
Script setup trước khi bắt đầu phiên làm việc
Hỗ trợ PyCharm và Google Colabx
"""

import subprocess
import sys
import os
from datetime import datetime


# Kiểm tra môi trường
def is_colab():
    """Kiểm tra có đang chạy trên Google Colab không"""
    try:
        import google.colab
        return True
    except ImportError:
        return False


def run_command(command, description, check_error=True):
    """Chạy command và hiển thị kết quả"""
    print(f"\n📌 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if check_error:
            print(f"❌ Lỗi: {e.stderr}")
            return None
        else:
            return e.stderr.strip()


def get_input(prompt, default=None):
    """Lấy input từ user với giá trị mặc định"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def setup_git_config():
    """Setup Git config nếu chưa có"""
    print("\n🔧 Kiểm tra Git configuration...")

    user_name = run_command("git config user.name", "Lấy Git username", check_error=False)
    user_email = run_command("git config user.email", "Lấy Git email", check_error=False)

    if not user_name or "not set" in user_name.lower():
        print("\n⚠️  Git user chưa được cấu hình")
        name = get_input("Nhập tên của bạn (VD: Nguyen Van A)")
        email = get_input("Nhập email (VD: nguyenvana@example.com)")

        run_command(f'git config user.name "{name}"', "Cấu hình Git username")
        run_command(f'git config user.email "{email}"', "Cấu hình Git email")
        print("✅ Đã cấu hình Git user")
    else:
        print(f"✅ Git user: {user_name} <{user_email}>")


def setup_colab():
    """Setup đặc biệt cho Google Colab"""
    print("\n🔍 Phát hiện môi trường Google Colab")

    # Mount Google Drive nếu chưa mount
    try:
        from google.colab import drive
        if not os.path.exists('/content/drive'):
            print("📁 Mount Google Drive...")
            drive.mount('/content/drive')
        else:
            print("✅ Google Drive đã được mount")
    except Exception as e:
        print(f"⚠️  Không thể mount Google Drive: {e}")

    # Hỏi đường dẫn project
    default_path = "/content/drive/MyDrive/project"
    project_path = get_input("Đường dẫn đến project trên Drive", default_path)

    if os.path.exists(project_path):
        os.chdir(project_path)
        print(f"✅ Đã chuyển đến: {project_path}")
    else:
        print(f"⚠️  Thư mục không tồn tại: {project_path}")
        create = get_input("Tạo thư mục mới? (y/n)", "n").lower()
        if create == 'y':
            os.makedirs(project_path, exist_ok=True)
            os.chdir(project_path)
            print(f"✅ Đã tạo và chuyển đến: {project_path}")
        else:
            print("❌ Hủy bỏ setup")
            sys.exit(1)


def main():
    print("=" * 70)
    print("🚀 SETUP PHIÊN LÀM VIỆC MỚI - NHÓM 5 NGƯỜI")
    print("=" * 70)

    # Setup cho Colab nếu cần
    if is_colab():
        setup_colab()
    else:
        print("\n💻 Môi trường: PyCharm/Local IDE")

    # Kiểm tra xem đang ở trong git repo
    git_check = run_command("git rev-parse --git-dir", "Kiểm tra Git repository", check_error=False)

    if not git_check or "not a git repository" in git_check.lower():
        print("\n⚠️  Chưa phải Git repository")
        init = get_input("Khởi tạo Git repository? (y/n)", "n").lower()

        if init == 'y':
            run_command("git init", "Khởi tạo Git repository")
            remote = get_input("Nhập URL remote repository (hoặc Enter để bỏ qua)")
            if remote:
                run_command(f"git remote add origin {remote}", "Thêm remote repository")
        else:
            print("❌ Cần có Git repository để tiếp tục")
            sys.exit(1)

    # Setup Git config
    setup_git_config()

    # Lấy thông tin branch hiện tại
    current_branch = run_command("git branch --show-current", "Lấy branch hiện tại")

    if not current_branch:
        print("\n⚠️  Chưa có branch nào. Tạo branch main...")
        run_command("git checkout -b main", "Tạo branch main")
        current_branch = "main"

    print(f"\n📍 Branch hiện tại: {current_branch}")

    # Kiểm tra uncommitted changes
    status = subprocess.check_output("git status --porcelain", shell=True, text=True)
    if status:
        print("\n⚠️  Có thay đổi chưa commit:")
        print(status[:500])  # Giới hạn hiển thị
        if len(status) > 500:
            print("... (còn nhiều thay đổi khác)")

        choice = get_input("Xử lý: (s)tash/(c)ommit/(i)gnore/(a)bort", "s").lower()

        if choice == 's':
            stash_msg = get_input("Tên stash (hoặc Enter để dùng mặc định)", "WIP")
            run_command(f'git stash save "{stash_msg}"', "Stash thay đổi hiện tại")
        elif choice == 'c':
            commit_msg = get_input("Nhập commit message")
            run_command("git add .", "Thêm tất cả thay đổi")
            run_command(f'git commit -m "{commit_msg}"', "Commit thay đổi")
        elif choice == 'i':
            print("⚠️  Bỏ qua thay đổi, tiếp tục...")
        else:
            print("❌ Hủy bỏ setup")
            sys.exit(0)

    # Kiểm tra remote
    remote_check = run_command("git remote -v", "Kiểm tra remote", check_error=False)
    if not remote_check or not remote_check.strip():
        print("\n⚠️  Chưa có remote repository")
        add_remote = get_input("Thêm remote? (y/n)", "n").lower()
        if add_remote == 'y':
            remote_url = get_input("Nhập URL remote repository")
            run_command(f"git remote add origin {remote_url}", "Thêm remote")

    # Pull code mới nhất từ remote
    if remote_check and remote_check.strip():
        main_branch = get_input("Branch chính để pull từ remote", "main")

        # Kiểm tra branch có tồn tại trên remote không
        remote_branches = run_command("git ls-remote --heads origin", "Kiểm tra remote branches", check_error=False)

        if remote_branches and main_branch in remote_branches:
            if current_branch != main_branch:
                checkout_main = get_input(f"Checkout về {main_branch}? (y/n)", "y").lower()
                if checkout_main == 'y':
                    if run_command(f"git checkout {main_branch}", f"Chuyển về branch {main_branch}"):
                        run_command(f"git pull origin {main_branch}", f"Pull code mới nhất từ {main_branch}")
                    current_branch = main_branch
            else:
                run_command(f"git pull origin {main_branch}", f"Pull code mới nhất từ {main_branch}")
        else:
            print(f"⚠️  Branch {main_branch} chưa có trên remote hoặc chưa có commits")

    # Hiển thị danh sách thành viên (gợi ý)
    print("\n👥 Thành viên nhóm gợi ý cho tên branch:")
    members = ["member1", "member2", "member3", "member4", "member5"]
    for i, member in enumerate(members, 1):
        print(f"   {i}. {member}")
    print("   (Bạn có thể chỉnh sửa trong code để thay tên thực)")

    # Tạo branch mới
    create_new = get_input("\nTạo branch mới? (y/n)", "y").lower()

    if create_new == 'y':
        # Đề xuất tên branch
        today = datetime.now().strftime("%Y%m%d")

        print("\n📝 Mẫu tên branch:")
        print(f"   1. feature/[tên-tính-năng]")
        print(f"   2. bugfix/[tên-lỗi]")
        print(f"   3. [tên-member]/[công-việc]")
        print(f"   4. dev-{today}")

        branch_name = get_input(f"Tên branch mới", f"dev-{today}")

        # Kiểm tra branch đã tồn tại chưa
        existing_branch = run_command(f"git rev-parse --verify {branch_name}", "Kiểm tra branch", check_error=False)

        if existing_branch and "fatal" not in existing_branch.lower():
            print(f"⚠️  Branch '{branch_name}' đã tồn tại")
            checkout = get_input(f"Checkout sang branch này? (y/n)", "y").lower()
            if checkout == 'y':
                run_command(f"git checkout {branch_name}", f"Chuyển sang branch {branch_name}")
        else:
            if run_command(f"git checkout -b {branch_name}", f"Tạo và chuyển sang branch {branch_name}"):
                print(f"✅ Đã tạo branch mới: {branch_name}")

    # Hiển thị trạng thái cuối cùng
    print("\n" + "=" * 70)
    print("✅ SETUP HOÀN TẤT!")
    print("=" * 70)

    current_branch = run_command("git branch --show-current", "Lấy branch hiện tại")
    print(f"📍 Branch hiện tại: {current_branch}")

    # Hiển thị danh sách branch
    print("\n📋 Các branch có sẵn:")
    run_command("git branch", "Liệt kê branches", check_error=False)

    # Hiển thị commit gần nhất
    print("\n📝 Commit gần nhất:")
    run_command("git log -1 --oneline", "Hiển thị commit cuối", check_error=False)

    print("\n💪 Sẵn sàng làm việc!")
    print("💡 Tip: Nhớ pull thường xuyên để cập nhật code từ team!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy bỏ setup")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)