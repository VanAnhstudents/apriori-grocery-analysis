#!/usr/bin/env python3
"""
Script đẩy code lên GitHub và tạo Pull Request - BẢN ĐÃ SỬA LỖI
Hỗ trợ PyCharm và Google Colab
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


def run_command(command, description, capture=True, check_error=True, return_output=False):
    """Chạy command và hiển thị kết quả - ĐÃ SỬA LỖI"""
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
            if result.stdout and not return_output:
                print(result.stdout)
            # Nếu cần output thực tế (như branch name), trả về stdout
            if return_output:
                return result.stdout.strip()
            # Ngược lại trả về "SUCCESS" để biết command thành công
            return "SUCCESS"
        else:
            # Với capture=False, chỉ chạy và hiển thị output real-time
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


def check_gh_cli():
    """Kiểm tra GitHub CLI đã cài đặt chưa"""
    try:
        subprocess.run(
            "gh --version",
            shell=True,
            check=True,
            capture_output=True
        )
        return True
    except:
        return False


def get_repo_info():
    """Lấy thông tin repository"""
    remote_url = run_command(
        "git config --get remote.origin.url",
        "Lấy remote URL",
        check_error=False
    )

    if not remote_url:
        return None

    # Parse GitHub repo info
    if "github.com" in remote_url:
        if remote_url.startswith("git@github.com:"):
            repo_path = remote_url.replace("git@github.com:", "").replace(".git", "")
        elif "https://github.com/" in remote_url:
            repo_path = remote_url.replace("https://github.com/", "").replace(".git", "")
        else:
            repo_path = None
        return repo_path
    return None


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
        print("💡 Nếu gặp lỗi authentication:")
        print("   1. Sử dụng Personal Access Token thay vì password")
        print("   2. Hoặc chuyển sang SSH: git remote set-url origin git@github.com:user/repo.git")


def setup_colab_git():
    """Setup Git cho Colab nếu cần"""
    if is_colab():
        print("\n🔍 Môi trường Google Colab")

        # Kiểm tra Git config
        user_name = run_command("git config user.name", "Lấy Git username", check_error=False)
        if not user_name or "not set" in str(user_name).lower():
            print("\n⚠️  Cần cấu hình Git user")
            name = get_input("Nhập tên của bạn")
            email = get_input("Nhập email")
            run_command(f'git config --global user.name "{name}"', "Cấu hình username")
            run_command(f'git config --global user.email "{email}"', "Cấu hình email")


def main():
    print("=" * 70)
    print("🚀 PUSH CODE VÀ TẠO PULL REQUEST - BẢN ĐÃ SỬA LỖI")
    print("=" * 70)

    # Setup cho Colab nếu cần
    setup_colab_git()
    check_git_auth()

    if not is_colab():
        print("\n💻 Môi trường: PyCharm/Local IDE")

    # Kiểm tra Git repository - SỬA: dùng check_error=False
    git_check = run_command("git rev-parse --git-dir", "Kiểm tra Git repository", check_error=False)
    if not git_check:
        print("❌ Không phải Git repository")
        sys.exit(1)

    # Lấy branch hiện tại
    current_branch = run_command(
        "git branch --show-current",
        "Lấy branch hiện tại"
    )

    if not current_branch:
        print("❌ Không thể xác định branch hiện tại")
        sys.exit(1)

    print(f"\n📍 Branch hiện tại: {current_branch}")

    # Kiểm tra remote
    remote_check = run_command("git remote -v", "Kiểm tra remote", check_error=False)
    if not remote_check:
        print("\n❌ Chưa có remote repository")
        add_remote = get_input("Thêm remote ngay? (y/n)", "y").lower()
        if add_remote == 'y':
            remote_url = get_input("Nhập URL remote repository")
            run_command(f"git remote add origin {remote_url}", "Thêm remote")
        else:
            print("❌ Cần có remote để push code")
            sys.exit(1)

    # Kiểm tra có thay đổi không
    status = run_command("git status --porcelain", "Kiểm tra trạng thái", check_error=False)

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
            print("❌ Hủy bỏ")
            sys.exit(0)
    else:
        print("\n📝 Các thay đổi:")
        status_lines = status.strip().split('\n') if status else []

        # Hiển thị tối đa 20 files
        for line in status_lines[:20]:
            print(f"   {line}")

        if len(status_lines) > 20:
            print(f"   ... và {len(status_lines) - 20} file(s) khác")

        # Review changes
        review = get_input("\nXem chi tiết thay đổi? (y/n)", "n").lower()
        if review == 'y':
            run_command("git diff --stat", "Thống kê thay đổi", capture=False, check_error=False)

        # Add all files - SỬA QUAN TRỌNG: Kiểm tra kết quả đúng cách
        add_all = get_input("\nThêm tất cả các thay đổi? (y/n)", "y").lower()

        if add_all == 'y':
            result = run_command("git add .", "Thêm tất cả các thay đổi")
            # CHỈ thoát nếu có lỗi (trả về None)
            if result is None:
                print("❌ Lỗi khi thêm files")
                sys.exit(1)
        else:
            files_to_add = get_input("Nhập files cần add (cách nhau bởi dấu cách)")
            result = run_command(f"git add {files_to_add}", "Thêm files đã chọn")
            if result is None:
                print("❌ Lỗi khi thêm files")
                sys.exit(1)

        # Commit
        print("\n💬 Mẫu commit message:")
        print("   - feat: thêm tính năng X")
        print("   - fix: sửa lỗi Y")
        print("   - docs: cập nhật tài liệu")
        print("   - refactor: tái cấu trúc code")
        print("   - test: thêm tests")

        commit_msg = get_input("\nNhập commit message")
        if not commit_msg:
            print("❌ Commit message không được để trống")
            sys.exit(1)

        # Thêm prefix với tên nếu muốn
        add_author = get_input("Thêm tên vào commit? (y/n)", "n").lower()
        if add_author == 'y':
            author_name = get_input("Tên của bạn (VD: member1)")
            commit_msg = f"[{author_name}] {commit_msg}"

        # SỬA: Kiểm tra kết quả commit đúng cách
        result = run_command(f'git commit -m "{commit_msg}"', "Commit thay đổi")
        if result is None:
            print("❌ Lỗi khi commit")
            sys.exit(1)

    # Pull trước khi push để tránh conflict
    print(f"\n🔄 Đồng bộ với remote...")
    pull_result = run_command(
        f"git pull origin {current_branch} --rebase",
        "Pull và rebase từ remote",
        check_error=False
    )

    if pull_result and "conflict" in pull_result.lower():
        print("\n⚠️  Có conflict! Cần giải quyết conflict trước khi push")
        print("Chạy: git status để xem files conflict")
        print("Sau khi giải quyết: git add . && git rebase --continue")
        sys.exit(1)

    # PUSH - PHẦN QUAN TRỌNG
    print(f"\n🚀 Push branch {current_branch} lên remote...")

    # Kiểm tra branch đã có trên remote chưa
    remote_exists = subprocess.run(
        f"git ls-remote --heads origin {current_branch}",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()

    if remote_exists:
        push_cmd = f"git push origin {current_branch}"
    else:
        push_cmd = f"git push -u origin {current_branch}"
        print(f"ℹ️  Branch mới, sẽ tạo trên remote")

    # Thực hiện push
    print(f"\n📌 Đang push code lên GitHub...")
    try:
        result = subprocess.run(push_cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ Push thành công!")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi push: {e.stderr}")
        print("❌ Push thất bại")
        print("\n💡 Một số giải pháp:")
        print("   1. Kiểm tra quyền truy cập repository")
        print("   2. Kiểm tra kết nối mạng")
        print("   3. Pull code mới nhất trước")
        sys.exit(1)

    print("✅ Push thành công!")

    # Lấy thông tin repo
    repo_info = get_repo_info()

    # Tạo Pull Request
    create_pr = get_input("\n🔀 Tạo Pull Request? (y/n)", "y").lower()

    if create_pr == 'y':
        # Kiểm tra GitHub CLI
        has_gh_cli = check_gh_cli()

        if not has_gh_cli:
            print("\n⚠️  GitHub CLI chưa được cài đặt")
            print("Cài đặt:")
            if is_colab():
                print(
                    "   !curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg")
                print(
                    "   !echo \"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main\" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null")
                print("   !sudo apt update && sudo apt install gh")
            else:
                print("   https://cli.github.com/")

            if repo_info:
                pr_url = f"https://github.com/{repo_info}/compare/{current_branch}?expand=1"
                print(f"\n🔗 Hoặc tạo PR thủ công tại:\n   {pr_url}")
            sys.exit(0)

        # Lấy thông tin PR
        base_branch = get_input("Base branch (merge vào)", "main")

        print("\n📝 Template commit message gần nhất để tham khảo:")
        recent_commit = run_command(
            "git log -1 --pretty=%B",
            "Lấy commit message",
            check_error=False
        )
        if recent_commit:
            print(f"   {recent_commit}")

        pr_title = get_input("\nTiêu đề PR", f"Pull request từ {current_branch}")

        print("\n💡 Mẫu mô tả PR:")
        print("   ## Thay đổi")
        print("   - Thêm/Sửa/Xóa X")
        print("   ## Testing")
        print("   - Đã test Y")
        print("   ## Screenshots (nếu có)")
        print("   - ...")

        pr_body = get_input("\nMô tả PR (Enter để bỏ qua)", "")

        # Tạo PR command
        pr_cmd = f'gh pr create --base {base_branch} --head {current_branch} --title "{pr_title}"'

        if pr_body:
            pr_cmd += f' --body "{pr_body}"'
        else:
            pr_cmd += ' --body ""'

        # Các options khác
        print("\n⚙️  Tùy chọn PR:")
        is_draft = get_input("Tạo Draft PR? (y/n)", "n").lower()
        if is_draft == 'y':
            pr_cmd += ' --draft'

        # Assign reviewers
        assign_reviewers = get_input("Assign reviewers? (y/n)", "n").lower()
        if assign_reviewers == 'y':
            reviewers = get_input("Nhập username reviewers (cách nhau bởi dấu phẩy)")
            if reviewers:
                pr_cmd += f' --reviewer {reviewers}'

        print("\n🔀 Đang tạo Pull Request...")
        result = run_command(pr_cmd, "Tạo PR trên GitHub")

        if result:
            print("\n✅ Tạo Pull Request thành công!")
            for line in result.split('\n'):
                if 'https://github.com' in line:
                    print(f"🔗 {line.strip()}")
        else:
            print("❌ Không thể tạo PR")
            if repo_info:
                pr_url = f"https://github.com/{repo_info}/compare/{current_branch}?expand=1"
                print(f"\n🔗 Tạo PR thủ công tại:\n   {pr_url}")
            sys.exit(1)

    # Hiển thị kết quả cuối cùng
    print("\n" + "=" * 70)
    print("✅ HOÀN TẤT!")
    print("=" * 70)
    print(f"📍 Branch: {current_branch}")
    print("✅ Code đã được push lên GitHub")

    if create_pr == 'y':
        print("✅ Pull Request đã được tạo")
        print("\n👥 Nhớ thông báo team review PR nhé!")

    # Hiển thị commit cuối
    print("\n📝 Commit vừa push:")
    run_command("git log -1 --oneline", "Hiển thị commit", check_error=False)

    print("\n🎉 Chúc mừng! Hãy nghỉ ngơi hoặc làm việc tiếp!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy bỏ")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)