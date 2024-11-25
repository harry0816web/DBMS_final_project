document.getElementById('login-form').addEventListener('submit', function (e) {
    e.preventDefault(); // 防止表單提交導致頁面刷新
  
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');
  
    errorMessage.textContent = ''; // 清空之前的錯誤訊息
  
    // 簡單驗證
    if (username === '' || password === '') {
      errorMessage.textContent = '請填寫所有欄位！';
      return;
    }
  
    // 模擬後端驗證
    if (username === 'admin' && password === '123456') {
      alert('登入成功！');
      // 可在此跳轉到主頁，例如：window.location.href = '/dashboard';
      window.location.href = 'file:///C:/Users/tuna9/Desktop/DBMS/final_project/final_project.html';
    } else {
      errorMessage.textContent = '用戶名或密碼錯誤！';
    }
  });
  