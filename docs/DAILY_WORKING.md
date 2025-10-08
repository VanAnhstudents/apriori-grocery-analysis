# 📋 QUY TRÌNH LÀM VIỆC HẰNG NGÀY

Hướng dẫn chi tiết cho một phiên làm việc với Git và Python, hỗ trợ PyCharm, VS Code và Google Colab.

---

## 🌅 BƯỚC 1: BẮT ĐẦU PHIÊN LÀM VIỆC

### Chạy Script Setup

```bash
python daily_setup.py
```

Script này sẽ tự động thực hiện các công việc sau:

### 1.1 Kiểm Tra Hệ Thống

- ✅ Kiểm tra phiên bản Python
- ✅ Kiểm tra pip có sẵn
- ✅ Kiểm tra Git đã cài đặt
- ✅ Kiểm tra dung lượng ổ đĩa (local)

### 1.2 Thiết Lập Môi Trường

**Đối với Google Colab:**
- Mount Google Drive tự động
- Chuyển đến thư mục project trên Drive
- Tạo thư mục mới nếu chưa tồn tại

**Đối với PyCharm/Local:**
- Làm việc trong thư mục hiện tại
- Kiểm tra cấu hình local

### 1.3 Cấu Hình Git

Script sẽ kiểm tra và thiết lập:
- Git username (nếu chưa có)
- Git email (nếu chưa có)
- Remote repository (nếu chưa có)

**Ví dụ cấu hình:**
```
Git username: Nguyen Van A
Git email: nguyenvana@example.com
```

### 1.4 Quản Lý Repository

**Nếu chưa phải Git repository:**
- Script sẽ hỏi có muốn khởi tạo Git repo không
- Thêm remote repository URL nếu có

**Nếu đã là Git repository:**
- Hiển thị branch hiện tại
- Kiểm tra các thay đổi chưa commit

### 1.5 Xử Lý Thay Đổi Chưa Commit

Nếu có thay đổi chưa commit, bạn có 4 lựa chọn:

| Tùy chọn | Mô tả | Khi nào dùng |
|----------|-------|--------------|
| **s** (stash) | Lưu tạm thay đổi | Muốn lưu công việc dở dang |
| **c** (commit) | Commit ngay | Thay đổi đã hoàn thành |
| **i** (ignore) | Bỏ qua | Tiếp tục với thay đổi hiện tại |
| **a** (abort) | Hủy setup | Muốn xử lý thủ công |

### 1.6 Đồng Bộ Code

- Pull code mới nhất từ branch chính (thường là `main`)
- Cập nhật local repository với remote

### 1.7 Cài Đặt Thư Viện

Script cung cấp 6 tùy chọn cài đặt thư viện:

#### Tùy chọn 1: Cơ Bản
```
numpy, pandas, matplotlib, seaborn,
requests, python-dotenv, tqdm
```

#### Tùy chọn 2: AI/ML
```
torch, torchvision, tensorflow, scikit-learn,
opencv-python, Pillow, transformers
```

#### Tùy chọn 3: Web Development
```
flask, django, fastapi, streamlit,
beautifulsoup4, selenium
```

#### Tùy chọn 4: Tất Cả
Cài đặt tất cả các thư viện ở trên

#### Tùy chọn 5: Tự Chọn
Nhập danh sách thư viện cần cài đặt

#### Tùy chọn 6: Bỏ Qua
Không cài đặt thư viện mới

**Ngoài ra:**
- Tự động cài đặt từ `requirements.txt` nếu có
- Cài đặt pre-commit hooks nếu có `.pre-commit-config.yaml`
- Cài đặt công cụ code quality (black, flake8, pytest) cho local
- Cài đặt công cụ Colab (jupyter, ipywidgets, plotly) cho Colab

### 1.8 Tạo Branch Mới

Script đề xuất các mẫu tên branch:

```
1. feature/[tên-tính-năng]     - Thêm tính năng mới
2. bugfix/[tên-lỗi]            - Sửa lỗi
3. [tên-member]/[công-việc]    - Branch cá nhân
4. dev-YYYYMMDD                - Branch dev theo ngày
```

**Ví dụ:**
- `feature/user-authentication`
- `bugfix/login-error`
- `member1/update-ui`
- `dev-20251008`

### 1.9 Kết Quả Setup

Sau khi hoàn tất, script hiển thị:
- ✅ Branch hiện tại
- 📋 Danh sách các branch có sẵn
- 📝 Commit gần nhất
- 📦 Các thư viện chính đã cài đặt

---

## 💻 BƯỚC 2: LÀM VIỆC

### 2.1 Coding

Thực hiện công việc của bạn:
- Viết code
- Test tính năng
- Fix bugs
- Refactor code

### 2.2 Thường Xuyên Pull

**Khuyến nghị:** Pull code từ remote mỗi 1-2 giờ

```bash
git pull origin main  # hoặc branch chính khác
```

### 2.3 Commit Nhỏ và Thường Xuyên

**Nguyên tắc commit tốt:**
- Commit sau mỗi tính năng nhỏ hoàn thành
- Commit message rõ ràng, mô tả đúng thay đổi
- Không commit quá nhiều thay đổi cùng lúc

**Ví dụ commit thủ công:**
```bash
git add .
git commit -m "feat: add user login validation"
```

---

## 🚀 BƯỚC 3: KẾT THÚC PHIÊN LÀM VIỆC

### Chạy Script Push

```bash
python push_to_github.py
```

### 3.1 Kiểm Tra Môi Trường

Script tự động:
- Phát hiện IDE đang sử dụng (Colab/VS Code/PyCharm/Terminal)
- Kiểm tra Git config
- Kiểm tra authentication method (HTTPS/SSH)

### 3.2 Kiểm Tra Repository

- Xác nhận đang trong Git repository
- Hiển thị branch hiện tại
- Kiểm tra remote có tồn tại không

### 3.3 Xử Lý Thay Đổi

**Nếu có thay đổi:**

1. **Xem danh sách files thay đổi**
   - Hiển thị tối đa 15 files
   - Có thể xem chi tiết với `git diff`

2. **Add files**
   - Add tất cả: chọn `y`
   - Add chọn lọc: chọn `n` và nhập tên files

3. **Commit message**
   
   Script đề xuất các prefix chuẩn:
   ```
   - feat:     thêm tính năng mới
   - fix:      sửa lỗi
   - docs:     cập nhật tài liệu
   - refactor: tái cấu trúc code
   - style:    sửa định dạng
   - test:     thêm tests
   ```

   **Ví dụ:**
   ```
   feat: add user authentication
   fix: resolve login timeout issue
   docs: update API documentation
   ```

4. **Thêm tên vào commit** (tùy chọn)
   ```
   [member1] feat: add user authentication
   ```

**Nếu không có thay đổi:**
- Kiểm tra commits chưa push
- Có thể chọn push commits đó hoặc bỏ qua

### 3.4 Đồng Bộ Trước Khi Push

Script tự động:
- Pull code mới nhất từ remote
- Phát hiện conflict nếu có
- Hướng dẫn giải quyết conflict

**Nếu có conflict:**
```bash
git status              # Xem files conflict
# Sửa conflict thủ công
git add .
git commit -m "Resolve conflicts"
```

### 3.5 Push Lên GitHub

Script tự động:
- Phát hiện branch mới hoặc đã tồn tại
- Sử dụng `git push -u` cho branch mới
- Sử dụng `git push` cho branch đã có

**Xử lý lỗi thông minh:**

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| Permission denied | Không có quyền push | Kiểm tra token/SSH key |
| could not read Username | Chưa authentication | Dùng Personal Access Token |
| failed to push | Remote có thay đổi mới | Pull trước, giải quyết conflict |
| non-fast-forward | Local lạc hậu | Pull và merge trước |

### 3.6 Kết Quả

Sau khi push thành công, script hiển thị:
- ✅ Trạng thái push
- 📝 Commit vừa push
- 🔗 Link đến GitHub repository
- 🔗 Link đến branch trên GitHub

---

## 📌 MẸO VÀ LƯU Ý

### Commit Message Tốt

**DO ✅**
```
feat: add user profile page
fix: resolve memory leak in image processing
docs: update installation guide
refactor: optimize database queries
```

**DON'T ❌**
```
update
fix bug
changes
wip
asdfasdf
```

### Quy Trình Tối Ưu

```
Sáng: Setup → Pull → Code → Commit thường xuyên
Trưa: Pull → Code → Commit
Chiều: Pull → Code → Commit
Tối: Push tất cả lên GitHub
```

### Branch Strategy

**Nên:**
- Mỗi tính năng một branch riêng
- Tên branch rõ ràng, mô tả công việc
- Merge về main khi hoàn thành

**Không nên:**
- Làm việc trực tiếp trên main
- Branch quá dài (>2 tuần)
- Tên branch vô nghĩa

### Authentication

**HTTPS (dùng Personal Access Token):**
```
Username: <github-username>
Password: <personal-access-token>
```

**SSH (khuyến nghị):**
```bash
# Đổi remote sang SSH
git remote set-url origin git@github.com:username/repo.git
```

### Xử Lý Conflict

```bash
# 1. Pull và phát hiện conflict
git pull origin main

# 2. Xem files conflict
git status

# 3. Sửa conflict thủ công trong files

# 4. Add và commit
git add .
git commit -m "Resolve merge conflicts"

# 5. Push
git push origin <your-branch>
```

---

## 🆘 XỬ LÝ SỰ CỐ

### Quên Stash

```bash
git stash list              # Xem danh sách stash
git stash apply             # Lấy lại stash gần nhất
git stash apply stash@{1}   # Lấy stash cụ thể
```

### Commit Nhầm

```bash
git reset HEAD~1            # Undo commit, giữ thay đổi
git reset --hard HEAD~1     # Undo commit, xóa thay đổi
```

### Push Nhầm

```bash
git revert <commit-hash>    # Tạo commit đảo ngược
git push origin <branch>    # Push commit revert
```

### Branch Nhầm

```bash
git stash                   # Lưu thay đổi
git checkout <correct-branch>  # Chuyển branch đúng
git stash pop               # Lấy lại thay đổi
```

---

## 📚 TÀI LIỆU THAM KHẢO

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com)
- [Conventional Commits](https://www.conventionalcommits.org)

---

## ✅ CHECKLIST HẰNG NGÀY

- [ ] Chạy `daily_setup.py` khi bắt đầu
- [ ] Pull code mới nhất
- [ ] Tạo branch mới cho công việc
- [ ] Commit thường xuyên với message rõ ràng
- [ ] Pull định kỳ trong ngày
- [ ] Chạy `push_to_github.py` khi kết thúc
- [ ] Kiểm tra code đã lên GitHub

---

**🎯 Mục tiêu:** Làm việc hiệu quả, code sạch, không bao giờ mất code!

**💡 Khẩu hiệu:** "Commit sớm, Commit thường xuyên, Push đều đặn!"