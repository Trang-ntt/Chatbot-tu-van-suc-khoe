// ======================================================
// DỮ LIỆU BỆNH
// ======================================================

const diseases = [
  {
    name: "Cảm cúm",
    symptoms: [
      "sốt",
      "ho",
      "đau họng",
      "đau đầu",
      "mệt mỏi",
      "ớn lạnh",
      "đau cơ",
    ],
    advice:
      "Bạn nên nghỉ ngơi nhiều, uống đủ nước ấm, giữ ấm cơ thể. Nếu sốt cao trên 38.5°C hoặc triệu chứng kéo dài trên 7 ngày, cần đến cơ sở y tế để kiểm tra.",
  },

  {
    name: "Viêm phổi",
    symptoms: ["sốt", "ho", "khó thở", "đau ngực", "mệt mỏi"],
    advice:
      "Bạn nên nghỉ ngơi, uống nhiều nước, giữ ấm cơ thể. Nếu khó thở hoặc sốt cao kéo dài, cần đến bệnh viện ngay.",
  },

  {
    name: "Hen suyễn",
    symptoms: ["khó thở", "ho", "khò khè", "nặng ngực", "mệt mỏi"],
    advice:
      "Bạn nên tránh tiếp xúc với bụi, khói thuốc, dị nguyên. Nếu khó thở nặng, cần dùng thuốc theo chỉ định bác sĩ.",
  },

  {
    name: "Viêm dạ dày",
    symptoms: ["đau bụng", "buồn nôn", "ợ chua", "chán ăn", "đầy bụng"],
    advice:
      "Bạn nên ăn uống điều độ, tránh đồ cay nóng, rượu bia. Nếu đau bụng dữ dội hoặc nôn ra máu, cần đi khám ngay.",
  },

  {
    name: "Loét dạ dày",
    symptoms: ["đau bụng", "buồn nôn", "ợ nóng", "chán ăn", "sụt cân"],
    advice:
      "Bạn nên ăn uống nhẹ nhàng, tránh stress. Nếu có dấu hiệu xuất huyết tiêu hóa, cần nhập viện khẩn cấp.",
  },

  {
    name: "Viêm gan",
    symptoms: ["mệt mỏi", "vàng da", "chán ăn", "buồn nôn", "đau bụng"],
    advice:
      "Bạn nên tránh uống rượu bia, ăn uống lành mạnh. Nếu vàng da hoặc mệt mỏi kéo dài, cần đi khám chuyên khoa gan.",
  },

  {
    name: "Sỏi thận",
    symptoms: ["đau lưng", "đau bụng", "tiểu buốt", "tiểu ra máu", "buồn nôn"],
    advice:
      "Bạn nên uống nhiều nước, hạn chế muối. Nếu đau dữ dội hoặc tiểu ra máu nhiều, cần đi khám ngay.",
  },

  {
    name: "Viêm bàng quang",
    symptoms: ["tiểu buốt", "tiểu nhiều lần", "đau bụng dưới", "sốt nhẹ"],
    advice:
      "Bạn nên uống nhiều nước, giữ vệ sinh cá nhân. Nếu tiểu ra máu hoặc sốt cao, cần đi khám bác sĩ.",
  },

  {
    name: "Viêm xoang",
    symptoms: ["nghẹt mũi", "sổ mũi", "đau đầu", "đau mặt", "mệt mỏi"],
    advice:
      "Bạn nên rửa mũi bằng nước muối sinh lý, giữ ấm cơ thể. Nếu đau đầu dữ dội hoặc sốt cao, cần đi khám.",
  },

  {
    name: "Viêm khớp",
    symptoms: ["đau khớp", "sưng khớp", "cứng khớp", "mệt mỏi"],
    advice:
      "Bạn nên vận động nhẹ nhàng, tránh mang vác nặng. Nếu khớp sưng đỏ hoặc đau kéo dài, cần đi khám chuyên khoa.",
  },

  {
    name: "Loãng xương",
    symptoms: ["đau lưng", "đau khớp", "dễ gãy xương", "mệt mỏi"],
    advice:
      "Bạn nên bổ sung canxi, vitamin D, tập luyện nhẹ nhàng. Nếu có gãy xương, cần điều trị ngay.",
  },

  {
    name: "Thiếu máu",
    symptoms: ["mệt mỏi", "chóng mặt", "da xanh xao", "khó thở", "đau đầu"],
    advice:
      "Bạn nên bổ sung thực phẩm giàu sắt, vitamin B12. Nếu triệu chứng nặng, cần đi khám để xét nghiệm máu.",
  },

  {
    name: "Đái tháo đường",
    symptoms: ["khát nước nhiều", "tiểu nhiều", "sụt cân", "mệt mỏi", "mờ mắt"],
    advice:
      "Bạn nên kiểm soát chế độ ăn uống, tập luyện đều đặn. Nếu đường huyết cao hoặc có biến chứng, cần đi khám ngay.",
  },

  {
    name: "Tăng huyết áp",
    symptoms: ["đau đầu", "chóng mặt", "mệt mỏi", "khó thở", "tim đập nhanh"],
    advice:
      "Bạn nên ăn nhạt, tập luyện thường xuyên. Nếu huyết áp quá cao hoặc đau ngực, cần đi cấp cứu.",
  },

  {
    name: "Đột quỵ",
    symptoms: ["yếu liệt tay chân", "nói khó", "méo miệng", "đau đầu dữ dội"],
    advice:
      "Đây là tình trạng cấp cứu. Cần gọi cấp cứu ngay để được điều trị kịp thời.",
  },

  {
    name: "Trầm cảm",
    symptoms: ["buồn bã", "mất ngủ", "mệt mỏi", "chán ăn", "mất hứng thú"],
    advice:
      "Bạn nên chia sẻ với người thân, duy trì thói quen lành mạnh. Nếu có ý nghĩ tự tử, cần tìm sự hỗ trợ y tế ngay.",
  },

  {
    name: "Lo âu",
    symptoms: ["bồn chồn", "khó ngủ", "tim đập nhanh", "mệt mỏi", "đau đầu"],
    advice:
      "Bạn nên tập thở sâu, thư giãn, hạn chế caffeine. Nếu lo âu kéo dài, cần đi khám chuyên khoa tâm lý.",
  },

  {
    name: "Viêm da",
    symptoms: ["ngứa", "phát ban", "đỏ da", "khô da"],
    advice:
      "Bạn nên giữ vệ sinh da, tránh gãi mạnh. Nếu da nổi mụn nước hoặc lan rộng, cần đi khám da liễu.",
  },

  {
    name: "Zona thần kinh",
    symptoms: ["phát ban", "mụn nước", "đau rát", "ngứa", "mệt mỏi"],
    advice:
      "Bạn nên giữ vệ sinh vùng da, tránh gãi. Nếu đau nhiều hoặc lan rộng, cần đi khám ngay.",
  },

  {
    name: "Suy giáp",
    symptoms: ["mệt mỏi", "tăng cân", "da khô", "rụng tóc", "lạnh tay chân"],
    advice:
      "Bạn nên đi khám nội tiết để kiểm tra chức năng tuyến giáp. Nếu triệu chứng kéo dài, cần điều trị theo chỉ định.",
  },

  {
    name: "Cường giáp",
    symptoms: ["sụt cân", "tim đập nhanh", "run tay", "mệt mỏi", "khó ngủ"],
    advice:
      "Bạn nên hạn chế chất kích thích, đi khám nội tiết để kiểm tra. Nếu tim đập nhanh hoặc khó thở, cần đi cấp cứu.",
  },

  {
    name: "Cảm lạnh",
    symptoms: ["ho", "đau họng", "sổ mũi", "nghẹt mũi", "mệt mỏi", "đau đầu"],
    advice:
      "Bạn nên nghỉ ngơi, uống nước ấm, giữ ấm cơ thể. Nếu ho hoặc nghẹt mũi kéo dài trên 7 ngày, cần đi khám bác sĩ.",
  },

  {
    name: "Viêm họng",
    symptoms: ["đau họng", "sốt", "ho", "khàn tiếng", "đau đầu", "mệt mỏi"],
    advice:
      "Bạn nên súc miệng bằng nước muối ấm, uống nhiều nước, hạn chế nói to. Nếu đau họng dữ dội, khó nuốt hoặc sốt cao, cần đi khám bác sĩ.",
  },

  {
    name: "Rối loạn tiêu hóa",
    symptoms: [
      "đau bụng",
      "buồn nôn",
      "nôn",
      "tiêu chảy",
      "đầy bụng",
      "chán ăn",
    ],
    advice:
      "Bạn nên ăn uống nhẹ nhàng, tránh đồ dầu mỡ, uống nhiều nước. Nếu tiêu chảy kéo dài trên 3 ngày hoặc có dấu hiệu mất nước, cần đi khám ngay.",
  },

  {
    name: "Táo bón",
    symptoms: ["táo bón", "đầy bụng", "đau bụng", "chán ăn"],
    advice:
      "Bạn nên tăng cường uống nước, bổ sung chất xơ từ rau quả, vận động nhẹ nhàng. Nếu táo bón kéo dài trên 1 tuần, cần đi khám.",
  },

  {
    name: "Dị ứng",
    symptoms: ["ngứa", "phát ban", "đỏ mắt", "sổ mũi", "nghẹt mũi"],
    advice:
      "Bạn nên tránh tiếp xúc với yếu tố gây dị ứng, giữ vệ sinh môi trường sống. Nếu khó thở hoặc nổi mẩn toàn thân, cần đi khám ngay.",
  },

  {
    name: "Đau đầu",
    symptoms: ["đau đầu", "chóng mặt", "mệt mỏi", "khó ngủ", "buồn nôn"],
    advice:
      "Bạn nên nghỉ ngơi ở nơi yên tĩnh, uống đủ nước. Nếu đau đầu dữ dội, kèm theo nôn ói hoặc rối loạn thị giác, cần đi khám ngay.",
  },

  {
    name: "Đau cơ xương khớp",
    symptoms: ["đau cơ", "đau khớp", "đau lưng", "đau cổ", "mệt mỏi"],
    advice:
      "Bạn nên nghỉ ngơi, tránh vận động quá sức. Nếu đau kéo dài trên 2 tuần hoặc sưng khớp, cần đi khám chuyên khoa.",
  },

  {
    name: "Viêm kết mạc",
    symptoms: ["đỏ mắt", "đau mắt", "ngứa", "mệt mỏi"],
    advice:
      "Bạn nên giữ vệ sinh mắt, tránh dụi mắt. Nếu mắt đỏ kéo dài trên 3 ngày hoặc có mủ, cần đi khám bác sĩ.",
  },

  {
    name: "Viêm tai",
    symptoms: ["đau tai", "sốt", "đau đầu", "mệt mỏi"],
    advice:
      "Bạn nên theo dõi tình trạng đau tai. Nếu đau nhiều, kèm sốt cao hoặc chảy dịch tai, cần đi khám ngay.",
  },

  {
    name: "Mất ngủ",
    symptoms: ["khó ngủ", "mệt mỏi", "đau đầu", "chóng mặt"],
    advice:
      "Bạn nên duy trì thói quen ngủ đúng giờ, hạn chế dùng thiết bị điện tử trước khi ngủ. Nếu mất ngủ kéo dài trên 2 tuần, cần đi khám.",
  },

  {
    name: "Bệnh hô hấp",
    symptoms: ["khó thở", "ho", "đau ngực", "mệt mỏi"],
    advice:
      "Nếu khó thở hoặc đau ngực xuất hiện đột ngột hoặc nghiêm trọng, cần tìm kiếm sự chăm sóc y tế ngay.",
  },
];

// ======================================================
// TRIỆU CHỨNG XUNG ĐỘT
// ======================================================

const symptomConflicts = {
  "tiêu chảy": ["táo bón"],
  "táo bón": ["tiêu chảy"],

  "tăng cân": ["sụt cân"],
  "sụt cân": ["tăng cân"],

  "khó ngủ": ["mất ngủ"],
  "mất ngủ": ["khó ngủ"],
};

// ======================================================
// XỬ LÝ TRIỆU CHỨNG XUNG ĐỘT
// ======================================================

function handleSymptomConflicts() {
  const checkboxes = document.querySelectorAll(
    '.symptoms input[type="checkbox"]',
  );

  checkboxes.forEach((cb) => {
    cb.addEventListener("change", () => {
      const conflicts = symptomConflicts[cb.value] || [];

      if (cb.checked) {
        // Khi chọn triệu chứng,
        // disable các triệu chứng xung đột
        conflicts.forEach((conflictSymptom) => {
          const conflictCheckbox = [...checkboxes].find(
            (c) => c.value === conflictSymptom,
          );

          if (conflictCheckbox) {
            conflictCheckbox.disabled = true;

            conflictCheckbox.parentElement.classList.add("disabled-symptom");
          }
        });
      } else {
        // Khi bỏ chọn,
        // bật lại triệu chứng xung đột
        conflicts.forEach((conflictSymptom) => {
          const conflictCheckbox = [...checkboxes].find(
            (c) => c.value === conflictSymptom,
          );

          if (conflictCheckbox) {
            conflictCheckbox.disabled = false;

            conflictCheckbox.parentElement.classList.remove("disabled-symptom");
          }
        });
      }
    });
  });
}

// ======================================================
// LẤY CÁC TRIỆU CHỨNG ĐÃ CHỌN
// ======================================================

function getSelectedSymptoms() {
  const checkboxes = document.querySelectorAll(
    '.symptoms input[type="checkbox"]:checked',
  );

  const symptoms = [];

  checkboxes.forEach((cb) => {
    symptoms.push(cb.value);
  });

  return symptoms;
}

// ======================================================
// PHÂN TÍCH TRIỆU CHỨNG
// KẾT NỐI BACKEND FASTAPI
// ======================================================

async function analyzeSymptoms() {
  // Lấy triệu chứng người dùng chọn
  const selectedSymptoms = getSelectedSymptoms();

  // Lấy thời gian xuất hiện triệu chứng
  const duration = Number(document.getElementById("duration").value);

  // Lấy mức độ triệu chứng
  const severityText = document.getElementById("severity").value;

  // Khu vực hiển thị kết quả
  const result = document.getElementById("result");

  // ----------------------------------------------------
  // KIỂM TRA CHƯA CHỌN TRIỆU CHỨNG
  // ----------------------------------------------------

  if (selectedSymptoms.length === 0) {
    result.style.display = "block";

    result.innerHTML = `
      <h2>⚠️ Thông báo</h2>

      <p>
        Vui lòng chọn ít nhất một triệu chứng.
      </p>
    `;

    return;
  }

  // ----------------------------------------------------
  // CHUYỂN MỨC ĐỘ SANG DẠNG SỐ
  //
  // Backend yêu cầu:
  // 1 = nhẹ
  // 2 = vừa
  // 3 = nặng
  // ----------------------------------------------------

  let severity = 1;

  if (severityText === "vừa") {
    severity = 2;
  }

  if (severityText === "nặng") {
    severity = 3;
  }

  // ----------------------------------------------------
  // CHUYỂN THỜI GIAN SANG SỐ NGÀY
  // ----------------------------------------------------

  const daysSince = duration;

  // ----------------------------------------------------
  // HIỂN THỊ TRẠNG THÁI ĐANG PHÂN TÍCH
  // ----------------------------------------------------

  result.style.display = "block";

  result.innerHTML = `
    <p>
      ⏳ Đang phân tích triệu chứng...
    </p>
  `;

  // ----------------------------------------------------
  // GỬI DỮ LIỆU ĐẾN BACKEND
  // ----------------------------------------------------

  try {
    const token = localStorage.getItem("healthbot_token");

    if (!token) {
      throw new Error("Bạn cần đăng nhập trước khi phân tích triệu chứng.");
    }

    const response = await fetch("/api/symptoms/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        symptoms: selectedSymptoms,
        severity: severity,
        days_since: daysSince,
      }),
    });
    // --------------------------------------------------
    // KIỂM TRA HTTP ERROR
    // --------------------------------------------------

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        throw new Error("Bạn cần đăng nhập trước khi phân tích triệu chứng.");
      }

      throw new Error(
        "Không thể kết nối đến máy chủ. Mã lỗi: " + response.status,
      );
    }

    // --------------------------------------------------
    // NHẬN JSON TỪ BACKEND
    // --------------------------------------------------

    const data = await response.json();

    const results = data.results || [];

    // --------------------------------------------------
    // KHÔNG CÓ KẾT QUẢ
    // --------------------------------------------------

    if (results.length === 0) {
      result.innerHTML = `
        <h2>📋 Kết quả phân tích</h2>

        <p>
          Chưa tìm thấy kết quả phù hợp.
        </p>
      `;

      return;
    }

    // --------------------------------------------------
    // LẤY % CAO NHẤT
    // --------------------------------------------------

    const topPercent = results[0].percent;

    // Lấy tất cả bệnh có cùng % cao nhất
    const topResults = results.filter((r) => r.percent === topPercent);

    // --------------------------------------------------
    // TẠO HTML KẾT QUẢ
    // --------------------------------------------------

    let html = `
      <h2>
        📋 Kết quả phân tích sơ bộ
      </h2>

      <p>
        Các triệu chứng bạn nhập:
        <strong>
          ${selectedSymptoms.join(", ")}
        </strong>
      </p>
    `;

    // --------------------------------------------------
    // TRƯỜNG HỢP CÓ NHIỀU BỆNH CÙNG % CAO NHẤT
    // --------------------------------------------------

    if (topResults.length > 1) {
      html += `
        <h3>
          Các kết quả có cùng mức độ phù hợp cao nhất
          (${topPercent}%):
        </h3>
      `;

      topResults.forEach((r) => {
        html += `
          <p>
            <strong>
              ${r.name}
            </strong>

            – ${r.percent}%

            <br>

            💡 Khuyến nghị:
            ${r.advice}
          </p>
        `;
      });
    } else {
      // ------------------------------------------------
      // CHỈ CÓ MỘT KẾT QUẢ CAO NHẤT
      // ------------------------------------------------

      const r = topResults[0];

      html += `
        <h3>
          Kết quả có khả năng phù hợp cao nhất:
        </h3>

        <p>
          <strong>
            ${r.name}
          </strong>

          – Mức độ phù hợp:
          ${r.percent}%
        </p>

        <h3>
          💡 Khuyến nghị
        </h3>

        <p>
          ${r.advice}
        </p>
      `;
    }

    // --------------------------------------------------
    // CẢNH BÁO NẾU TRIỆU CHỨNG NẶNG / KÉO DÀI
    // --------------------------------------------------

    if (severity === 3 || daysSince >= 8) {
      html += `
        <div class="warning">

          ⚠️ Triệu chứng có mức độ nặng
          hoặc kéo dài.

          Bạn nên cân nhắc đến cơ sở y tế
          để được kiểm tra.

        </div>
      `;
    }

    // --------------------------------------------------
    // LƯU Ý Y TẾ
    // --------------------------------------------------

    html += `
      <div class="warning">

        ℹ️ Kết quả trên chỉ mang tính chất tham khảo,
        không thay thế chẩn đoán của bác sĩ.

      </div>

      <button
        id="reloadBtn"
        class="reload"
      >
        🔄 Tải lại để nhập mới
      </button>
    `;

    // --------------------------------------------------
    // HIỂN THỊ KẾT QUẢ
    // --------------------------------------------------

    result.innerHTML = html;

    // --------------------------------------------------
    // NÚT NHẬP LẠI
    // --------------------------------------------------

    const reloadBtn = document.getElementById("reloadBtn");

    if (reloadBtn) {
      reloadBtn.addEventListener("click", () => {
        location.reload();
      });
    }
  } catch (error) {
    // --------------------------------------------------
    // XỬ LÝ LỖI
    // --------------------------------------------------

    result.innerHTML = `
      <h2>
        ❌ Lỗi
      </h2>

      <p>
        ${error.message}
      </p>
    `;
  }
}

// ======================================================
// KHỞI ĐỘNG KHI TRANG ĐƯỢC MỞ
// ======================================================

document.addEventListener("DOMContentLoaded", handleSymptomConflicts);
