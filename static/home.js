// =====================================================
// HEALTHBOT - HOME.JS
// =====================================================

// =====================================================
// LẤY TOKEN
// =====================================================

function getToken() {
  return (
    localStorage.getItem("token") ||
    localStorage.getItem("access_token") ||
    localStorage.getItem("jwt") ||
    localStorage.getItem("healthbot_token")
  );
}

// =====================================================
// LẤY THÔNG TIN NGƯỜI DÙNG
// =====================================================

async function loadUserInfo() {
  const token = getToken();

  if (!token) {
    console.log("Chưa có token đăng nhập.");
    return;
  }

  try {
    const response = await fetch("/api/me", {
      method: "GET",

      headers: {
        Authorization: "Bearer " + token,
      },
    });

    if (!response.ok) {
      return;
    }

    const user = await response.json();

    const userName = document.getElementById("userName");

    const welcomeName = document.getElementById("welcomeName");

    const userRole = document.getElementById("userRole");

    const avatar = document.getElementById("userAvatar");

    const name = user.FullName || user.full_name || "Người dùng";

    if (userName) {
      userName.textContent = name;
    }

    if (welcomeName) {
      welcomeName.textContent = name;
    }

    if (userRole) {
      userRole.textContent =
        user.Role === "admin" ? "Quản trị viên" : "Thành viên";
    }

    if (avatar) {
      avatar.textContent = name.charAt(0).toUpperCase();
    }
  } catch (error) {
    console.error("Không thể lấy thông tin người dùng:", error);
  }
}

// =====================================================
// XUẤT BÁO CÁO
// =====================================================

async function exportReport() {
  const token = getToken();

  if (!token) {
    alert("Bạn chưa đăng nhập. Vui lòng đăng nhập lại.");

    window.location.href = "/";

    return;
  }

  try {
    const response = await fetch("/api/export/mine", {
      method: "GET",

      headers: {
        Authorization: "Bearer " + token,
      },
    });

    // =============================================
    // KIỂM TRA LỖI
    // =============================================

    if (!response.ok) {
      let message = "Không thể xuất báo cáo.";

      try {
        const data = await response.json();

        if (data.detail) {
          message = data.detail;
        }
      } catch (e) {
        // Không có JSON lỗi
      }

      alert(message);

      return;
    }

    // =============================================
    // NHẬN FILE
    // =============================================

    const blob = await response.blob();

    // =============================================
    // TẠO LINK DOWNLOAD
    // =============================================

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");

    a.href = url;

    a.download = "HealthBot_BaoCao.xlsx";

    document.body.appendChild(a);

    a.click();

    a.remove();

    window.URL.revokeObjectURL(url);

    alert("Đã xuất báo cáo thành công!");
  } catch (error) {
    console.error("Lỗi xuất báo cáo:", error);

    alert("Có lỗi xảy ra khi xuất báo cáo.");
  }
}

// =====================================================
// GẮN SỰ KIỆN NÚT XUẤT BÁO CÁO
// =====================================================

function setupExportButtons() {
  const sidebarButton = document.getElementById("exportReportBtn");

  const mainButton = document.getElementById("exportReportMainBtn");

  if (sidebarButton) {
    sidebarButton.addEventListener("click", exportReport);
  }

  if (mainButton) {
    mainButton.addEventListener("click", exportReport);
  }
}

// =====================================================
// THÔNG BÁO
// =====================================================

async function loadNotifications() {
  const token = getToken();

  if (!token) {
    return;
  }

  try {
    const response = await fetch("/api/notifications/mine", {
      headers: {
        Authorization: "Bearer " + token,
      },
    });

    if (!response.ok) {
      return;
    }

    const notifications = await response.json();

    const count = notifications.filter(
      (item) => item.Status === "unread",
    ).length;

    const badge = document.getElementById("notificationCount");

    if (badge) {
      if (count > 0) {
        badge.textContent = count;

        badge.style.display = "flex";
      } else {
        badge.style.display = "none";
      }
    }
  } catch (error) {
    console.error("Không thể tải thông báo:", error);
  }
}

// =====================================================
// ĐĂNG XUẤT
// =====================================================

function setupLogout() {
  const logoutButton = document.getElementById("logoutBtn");

  if (!logoutButton) {
    return;
  }

  logoutButton.addEventListener("click", function () {
    localStorage.removeItem("token");
    localStorage.removeItem("access_token");
    localStorage.removeItem("jwt");
    localStorage.removeItem("healthbot_token");

    window.location.href = "/";
  });
}

// =====================================================
// KHỞI ĐỘNG
// =====================================================

document.addEventListener("DOMContentLoaded", function () {
  loadUserInfo();

  loadNotifications();

  setupExportButtons();

  setupLogout();
});
