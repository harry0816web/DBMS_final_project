document.getElementById('register-form').addEventListener('submit', function (e) {
    e.preventDefault(); // 防止表單提交刷新頁面
  
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const errorMessage = document.getElementById('error-message');
  
    errorMessage.textContent = ''; // 清空之前的錯誤訊息
  
    // 簡單驗證
    if (username === '' || email === '' || password === '' || confirmPassword === '') {
      errorMessage.textContent = '所有欄位均為必填！';
      return;
    }
  
    if (password.length < 6) {
      errorMessage.textContent = '密碼長度至少為 6 個字符！';
      return;
    }
  
    if (password !== confirmPassword) {
      errorMessage.textContent = '密碼與確認密碼不符！';
      return;
    }
  
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errorMessage.textContent = '請輸入有效的電子郵件地址！';
      return;
    }
  
    alert('註冊成功！');
    // 在這裡可以將資料傳送到後端，例如：
    // fetch('/api/register', { method: 'POST', body: JSON.stringify({ username, email, password }) });
    window.location.href = 'C:\Users\tuna9\Desktop\DBMS\final_project\final_project.html';
  });
  