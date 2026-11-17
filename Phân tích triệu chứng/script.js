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

  {
    name: "Bệnh Alzheimer",
    symptoms: ["hay quên", "lú lẫn", "khó tập trung", "thay đổi tính cách"],
    ageMin: 60,
    ageMax: 120,
    advice:
      "Alzheimer thường gặp ở người lớn tuổi nhưng không chỉ xảy ra ở nhóm tuổi này. Cần được bác sĩ đánh giá; lú lẫn xuất hiện đột ngột cần cấp cứu.",
  },
  {
    name: "Sa sút trí tuệ",
    symptoms: ["hay quên", "lú lẫn", "khó tập trung"],
    ageMin: 60,
    ageMax: 120,
    advice:
      "Hay quên có nhiều nguyên nhân và không đồng nghĩa với sa sút trí tuệ. Nên khám nếu tình trạng tiến triển hoặc ảnh hưởng sinh hoạt.",
  },
  {
    name: "Loãng xương",
    symptoms: ["đau lưng", "đau khớp", "dễ gãy xương"],
    ageMin: 50,
    ageMax: 120,
    advice:
      "Nguy cơ loãng xương tăng theo tuổi nhưng không thể xác định chỉ qua triệu chứng. Nên trao đổi với bác sĩ về đánh giá nguy cơ.",
  },
  {
    name: "Bệnh tim mạch",
    symptoms: ["đau ngực", "khó thở", "tim đập nhanh", "mệt mỏi"],
    ageMin: 0,
    ageMax: 120,
    advice:
      "Các triệu chứng có nhiều nguyên nhân. Đau ngực mới xuất hiện, khó thở nặng hoặc ngất cần được cấp cứu.",
  },
  {
    name: "Trào ngược dạ dày - thực quản",
    symptoms: ["ợ chua", "ợ nóng", "đau bụng", "khàn tiếng"],
    ageMin: 0,
    ageMax: 120,
    advice:
      "Theo dõi triệu chứng và trao đổi với nhân viên y tế nếu tái diễn. Không tự cho rằng đau ngực là do trào ngược.",
  },
  {
    name: "Đau nửa đầu",
    symptoms: ["đau đầu", "buồn nôn", "mờ mắt"],
    ageMin: 0,
    ageMax: 120,
    advice:
      "Nếu đau đầu đột ngột dữ dội, kèm yếu liệt hoặc rối loạn ý thức, cần cấp cứu.",
  },
  {
    name: "Tay chân miệng",
    symptoms: ["sốt", "phát ban", "mụn nước", "đau họng", "chán ăn"],
    ageMin: 0,
    ageMax: 10,
    advice:
      "Bệnh thường gặp ở trẻ nhỏ nhưng không chỉ giới hạn ở trẻ. Trẻ lừ đừ, giật mình bất thường hoặc khó thở cần được khám ngay.",
  },
  {
    name: "Thủy đậu",
    symptoms: ["sốt", "phát ban", "mụn nước", "ngứa", "mệt mỏi"],
    ageMin: 0,
    ageMax: 120,
    advice:
      "Phát ban và mụn nước có nhiều nguyên nhân. Hãy liên hệ cơ sở y tế để được đánh giá, nhất là khi mang thai hoặc suy giảm miễn dịch.",
  },
  {
    name: "Viêm tai giữa ở trẻ em",
    symptoms: ["đau tai", "sốt", "khó ngủ", "chán ăn"],
    ageMin: 0,
    ageMax: 12,
    advice:
      "Đau tai và sốt ở trẻ cần được đánh giá phù hợp với tuổi. Không tự ý sử dụng kháng sinh.",
  },
  {
    name: "Trào ngược dạ dày ở trẻ sơ sinh",
    symptoms: ["nôn", "chán ăn"],
    ageMin: 0,
    ageMax: 1,
    advice:
      "Nôn ở trẻ sơ sinh có nhiều nguyên nhân. Nôn màu xanh, có máu, khó thở hoặc li bì cần được chăm sóc y tế khẩn cấp.",
  },
];

/* =========================================
   ĐỘ TUỔI THAM KHẢO CHO TỪNG BỆNH
   Dùng cho bài tập phân tích triệu chứng.
   Đây không phải tiêu chuẩn chẩn đoán y khoa.
========================================= */

// Mặc định: bệnh có thể gặp ở nhiều độ tuổi.
// Chỉ thu hẹp tuổi với những bệnh có nhóm tuổi tham khảo rõ hơn.
const ageRanges = {
  "Cảm cúm": [0, 120],
  "Viêm phổi": [0, 120],
  "Hen suyễn": [0, 120],
  "Viêm dạ dày": [0, 120],
  "Loét dạ dày": [0, 120],
  "Viêm gan": [0, 120],
  "Sỏi thận": [0, 120],
  "Viêm bàng quang": [0, 120],
  "Viêm xoang": [0, 120],
  "Viêm khớp": [0, 120],
  "Loãng xương": [50, 120],
  "Thiếu máu": [0, 120],
  "Đái tháo đường": [0, 120],
  "Tăng huyết áp": [18, 120],
  "Đột quỵ": [0, 120],
  "Trầm cảm": [0, 120],
  "Lo âu": [0, 120],
  "Viêm da": [0, 120],
  "Zona thần kinh": [0, 120],
  "Suy giáp": [0, 120],
  "Cường giáp": [0, 120],
  "Cảm lạnh": [0, 120],
  "Viêm họng": [0, 120],
  "Rối loạn tiêu hóa": [0, 120],
  "Táo bón": [0, 120],
  "Dị ứng": [0, 120],
  "Đau đầu": [0, 120],
  "Đau cơ xương khớp": [0, 120],
  "Viêm kết mạc": [0, 120],
  "Viêm tai": [0, 120],
  "Mất ngủ": [0, 120],
  "Bệnh hô hấp": [0, 120],

  // Nhóm bệnh thường liên quan nhiều hơn đến tuổi cao.
  // Tuổi thấp hơn vẫn có thể mắc một số dạng bệnh tương ứng.
  "Bệnh Alzheimer": [60, 120],
  "Sa sút trí tuệ": [60, 120],

  "Bệnh tim mạch": [0, 120],
  "Trào ngược dạ dày - thực quản": [0, 120],
  "Đau nửa đầu": [0, 120],

  // Nhóm bệnh thường gặp ở trẻ em.
  "Tay chân miệng": [0, 12],
  "Thủy đậu": [0, 120],
  "Viêm tai giữa ở trẻ em": [0, 12],
  "Trào ngược dạ dày ở trẻ sơ sinh": [0, 1],
};

// Áp dụng độ tuổi tham khảo vào dữ liệu từng bệnh
diseases.forEach((disease) => {
  const range = ageRanges[disease.name];

  if (range) {
    disease.ageMin = range[0];
    disease.ageMax = range[1];
  } else {
    // Nếu thêm bệnh mới mà chưa khai báo độ tuổi
    disease.ageMin = 0;
    disease.ageMax = 120;
  }
});

// Định nghĩa triệu chứng xung đột
const symptomConflicts = {
  "tiêu chảy": ["táo bón"],
  "táo bón": ["tiêu chảy"],
  "tăng cân": ["sụt cân"],
  "sụt cân": ["tăng cân"],
  "khó ngủ": ["mất ngủ"],
  "mất ngủ": ["khó ngủ"],
};

// Hàm xử lý xung đột khi chọn triệu chứng
function handleSymptomConflicts() {
  const checkboxes = document.querySelectorAll(
    '.symptoms input[type="checkbox"]',
  );

  checkboxes.forEach((cb) => {
    cb.addEventListener("change", () => {
      const conflicts = symptomConflicts[cb.value] || [];

      if (cb.checked) {
        // Khi chọn triệu chứng, disable và gạch ngang các triệu chứng xung đột
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
        // Khi bỏ chọn, bật lại và bỏ gạch ngang các triệu chứng xung đột
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

// Lấy triệu chứng đã chọn
function getSelectedSymptoms() {
  const checkboxes = document.querySelectorAll(
    '.symptoms input[type="checkbox"]:checked',
  );
  const symptoms = [];
  checkboxes.forEach((cb) => symptoms.push(cb.value));
  return symptoms;
}

// Phân tích triệu chứng

function analyzeSymptoms() {
  const selectedSymptoms = getSelectedSymptoms();
  const ageInput = document.getElementById("age");
  const duration = Number(document.getElementById("duration").value);
  const severity = document.getElementById("severity").value;
  const result = document.getElementById("result");

  // 1. Kiểm tra tuổi
  const age = Number(ageInput.value);

  if (
    ageInput.value.trim() === "" ||
    !Number.isInteger(age) ||
    age < 0 ||
    age > 120
  ) {
    result.style.display = "block";
    result.innerHTML = `
      <h2>Thông báo</h2>
      <p>Vui lòng nhập tuổi hợp lệ từ 0 đến 120.</p>
    `;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }

  // 2. Kiểm tra triệu chứng
  if (selectedSymptoms.length === 0) {
    result.style.display = "block";
    result.innerHTML = `
      <h2>Thông báo</h2>
      <p>Vui lòng chọn ít nhất một triệu chứng.</p>
    `;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }

  // 3. Các dấu hiệu nguy hiểm cần lưu ý
  const emergencySymptoms = [
    "khó thở",
    "đau ngực",
    "yếu liệt tay chân",
    "nói khó",
    "méo miệng",
    "đau đầu dữ dội",
  ];

  const emergencyFound = selectedSymptoms.filter((symptom) =>
    emergencySymptoms.includes(symptom),
  );

  // 4. Phân tích triệu chứng và độ tuổi
  const results = diseases
    .map((disease) => {
      const matchedSymptoms = selectedSymptoms.filter((symptom) =>
        disease.symptoms.includes(symptom),
      );

      // Bỏ qua bệnh không có triệu chứng trùng
      if (matchedSymptoms.length === 0) return null;

      // Lấy giới hạn độ tuổi của bệnh
      const ageMin = disease.ageMin ?? 0;
      const ageMax = disease.ageMax ?? 120;

      // Kiểm tra người dùng có nằm trong độ tuổi tham khảo không
      const ageMatches = age >= ageMin && age <= ageMax;

      // Tính điểm trùng khớp
      const percent = Math.round(
        (matchedSymptoms.length / disease.symptoms.length) * 100,
      );

      return {
        name: disease.name,
        percent,
        matchedSymptoms,
        ageMatches,
        ageMin,
        ageMax,
        advice: disease.advice,
      };
    })
    .filter((disease) => disease !== null);

  // Chỉ giữ các bệnh phù hợp với độ tuổi
  const ageFilteredResults = results.filter((disease) => disease.ageMatches);

  // Sắp xếp điểm từ cao xuống thấp
  ageFilteredResults.sort(
    (a, b) =>
      b.percent - a.percent ||
      b.matchedSymptoms.length - a.matchedSymptoms.length,
  );

  // 5. Hiển thị kết quả
  let html = `
    <h2>Kết quả phân tích sơ bộ</h2>
    <p><strong>Tuổi:</strong> ${age}</p>
    <p>
      <strong>Triệu chứng đã chọn:</strong>
      ${selectedSymptoms.join(", ")}
    </p>
    <p>
      Điểm trùng khớp chỉ dùng để xếp hạng gợi ý,
      không phải xác suất mắc bệnh hay kết quả chẩn đoán.
    </p>
  `;

  // Cảnh báo dấu hiệu nguy hiểm
  if (emergencyFound.length > 0) {
    html += `
      <div class="warning">
        <strong>Cảnh báo:</strong>
        Bạn đã chọn dấu hiệu ${emergencyFound.join(", ")}.
        Nếu dấu hiệu xuất hiện đột ngột hoặc nghiêm trọng,
        hãy gọi cấp cứu hoặc đến cơ sở y tế ngay.
        Không chờ kết quả từ ứng dụng.
      </div>
    `;
  }

  // Không có bệnh nào khớp triệu chứng
  if (results.length === 0) {
    html += `
      <h3>Chưa có gợi ý phù hợp</h3>
      <p>
        Chưa tìm thấy bệnh nào trong dữ liệu có triệu chứng trùng khớp.
        Điều này không có nghĩa là bạn không mắc bệnh.
        Hãy đi khám nếu triệu chứng kéo dài hoặc khiến bạn lo lắng.
      </p>
    `;
  }
  // Có bệnh khớp triệu chứng nhưng không phù hợp độ tuổi
  else if (ageFilteredResults.length === 0) {
    html += `
      <h3>Chưa có gợi ý phù hợp với độ tuổi</h3>
      <p>
        Các bệnh có triệu chứng trùng khớp trong dữ liệu hiện tại
        không nằm trong nhóm tuổi tham khảo của bạn.
        Ứng dụng chưa thể đưa ra gợi ý phù hợp.
        Điều này không có nghĩa là bạn không mắc bệnh.
      </p>
    `;
  }
  // Có bệnh phù hợp độ tuổi
  else {
    // Lấy điểm cao nhất
    const highestPercent = ageFilteredResults[0].percent;

    // Lấy tất cả bệnh đồng hạng cao nhất
    const bestResults = ageFilteredResults.filter(
      (disease) => disease.percent === highestPercent,
    );

    if (bestResults.length === 1) {
      // Chỉ có một bệnh đạt điểm cao nhất
      const disease = bestResults[0];

      html += `
        <h3>Gợi ý phù hợp nhất</h3>

        <div class="disease-result">
          <h3>${disease.name}</h3>

          <p>
            <strong>Điểm trùng khớp tham khảo:</strong>
            ${disease.percent}%
          </p>

          <p>
            <strong>Triệu chứng trùng:</strong>
            ${disease.matchedSymptoms.join(", ")}
          </p>

          <p>
            <strong>Độ tuổi:</strong>
            Bạn nằm trong nhóm tuổi tham khảo
            (${disease.ageMin}–${disease.ageMax} tuổi).
          </p>

          <p>
            <strong>Khuyến nghị:</strong>
            ${disease.advice}
          </p>
        </div>
      `;
    } else {
      // Có nhiều bệnh cùng điểm cao nhất
      html += `
        <h3>Các khả năng cần xem xét</h3>

        <p>
          Chương trình chưa phân biệt được rõ giữa các bệnh dưới đây.
          Các bệnh có cùng điểm trùng khớp cao nhất là
          <strong>${highestPercent}%</strong>:
        </p>
      `;

      bestResults.forEach((disease) => {
        html += `
          <div class="disease-result">
            <h3>${disease.name}</h3>

            <p>
              <strong>Điểm trùng khớp tham khảo:</strong>
              ${disease.percent}%
            </p>

            <p>
              <strong>Triệu chứng trùng:</strong>
              ${disease.matchedSymptoms.join(", ")}
            </p>

            <p>
              <strong>Độ tuổi:</strong>
              Bạn nằm trong nhóm tuổi tham khảo
              (${disease.ageMin}–${disease.ageMax} tuổi).
            </p>

            <p>
              <strong>Khuyến nghị:</strong>
              ${disease.advice}
            </p>
          </div>
        `;
      });

      html += `
        <p>
          Bạn có thể đang gặp vấn đề liên quan đến một trong các
          bệnh được gợi ý, nhưng chưa thể xác định bệnh chỉ qua
          triệu chứng. Hãy tham khảo ý kiến bác sĩ khi cần.
        </p>
      `;
    }
  }

  // 6. Cảnh báo khi triệu chứng nặng hoặc kéo dài
  if (severity === "nặng" || duration >= 8) {
    html += `
      <div class="warning">
        Triệu chứng được đánh giá là nặng hoặc kéo dài trên 7 ngày.
        Bạn nên được nhân viên y tế đánh giá.
      </div>
    `;
  }

  // 7. Thông báo an toàn và nút nhập lại
  html += `
    <div class="warning">
      Kết quả chỉ mang tính tham khảo, không thay thế chẩn đoán
      của bác sĩ. Điểm trùng khớp cao nhất không có nghĩa là
      bạn chắc chắn mắc bệnh đó.
    </div>

    <button id="reloadBtn" class="reload" type="button">
      Tải lại để nhập mới
    </button>
  `;

  result.innerHTML = html;
  result.style.display = "block";

  result.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });

  // 8. Làm mới biểu mẫu khi nhấn nút
  document.getElementById("reloadBtn").addEventListener("click", () => {
    document
      .querySelectorAll('.symptoms input[type="checkbox"]')
      .forEach((checkbox) => {
        checkbox.checked = false;
        checkbox.disabled = false;
      });

    // Bỏ trạng thái vô hiệu hóa của các triệu chứng
    document.querySelectorAll(".symptom-card").forEach((card) => {
      card.classList.remove("disabled-symptom");
    });

    ageInput.value = "";
    document.getElementById("duration").selectedIndex = 0;
    document.getElementById("severity").selectedIndex = 0;

    result.innerHTML = "";
    result.style.display = "none";

    // Cập nhật số lượng triệu chứng đã chọn nếu có giao diện này
    const selectedCount = document.getElementById("selectedCount");
    const selectedTags = document.getElementById("selectedTags");

    if (selectedCount) {
      selectedCount.textContent = "Đã chọn 0 triệu chứng";
    }

    if (selectedTags) {
      selectedTags.replaceChildren();
    }
  });
}

// Gọi hàm xử lý xung đột khi load trang
document.addEventListener("DOMContentLoaded", () => {
  handleSymptomConflicts();
  setupSymptomPicker();
  document
    .getElementById("analyzeButton")
    .addEventListener("click", analyzeSymptoms);
});

// Giao diện tìm kiếm, lọc nhóm và hiển thị triệu chứng đã chọn
function setupSymptomPicker() {
  const searchInput = document.getElementById("symptomSearch");
  const filters = document.querySelectorAll(".category-chip");
  const cards = [...document.querySelectorAll(".symptom-card")];
  const countLabel = document.getElementById("selectedCount");
  const selectedTags = document.getElementById("selectedTags");
  const noResults = document.getElementById("noSymptomsFound");
  let activeCategory = "Tất cả";

  function updateVisibility() {
    const query = searchInput.value.trim().toLocaleLowerCase("vi");
    let visible = 0;
    cards.forEach((card) => {
      const category = card.dataset.category;
      const searchText = (
        card.dataset.search +
        " " +
        card.innerText
      ).toLocaleLowerCase("vi");
      const matchesCategory =
        activeCategory === "Tất cả" || category === activeCategory;
      const matchesSearch = searchText.includes(query);
      const show = matchesCategory && matchesSearch;
      card.hidden = !show;
      if (show) visible++;
    });
    noResults.hidden = visible !== 0;
  }

  function updateSelected() {
    const checked = [
      ...document.querySelectorAll('.symptoms input[type="checkbox"]:checked'),
    ];
    countLabel.textContent = `Đã chọn ${checked.length} triệu chứng`;
    selectedTags.replaceChildren();
    checked.forEach((checkbox) => {
      const tag = document.createElement("button");
      tag.type = "button";
      tag.className = "selected-tag";
      tag.textContent = `${checkbox.value} ×`;
      tag.title = `Bỏ chọn ${checkbox.value}`;
      tag.addEventListener("click", () => {
        checkbox.checked = false;
        checkbox.dispatchEvent(new Event("change", { bubbles: true }));
        updateSelected();
      });
      selectedTags.appendChild(tag);
    });
  }

  searchInput.addEventListener("input", updateVisibility);
  filters.forEach((button) =>
    button.addEventListener("click", () => {
      activeCategory = button.dataset.category;
      filters.forEach((item) =>
        item.classList.toggle("active", item === button),
      );
      updateVisibility();
    }),
  );
  cards.forEach((card) =>
    card.querySelector("input").addEventListener("change", updateSelected),
  );
  document.getElementById("clearFilters").addEventListener("click", () => {
    searchInput.value = "";
    activeCategory = "Tất cả";
    filters.forEach((item) =>
      item.classList.toggle("active", item.dataset.category === activeCategory),
    );
    updateVisibility();
  });
  document.getElementById("clearSelected").addEventListener("click", () => {
    cards.forEach((card) => {
      const checkbox = card.querySelector("input");
      checkbox.checked = false;
      checkbox.disabled = false;
      card.classList.remove("disabled-symptom");
    });
    document
      .querySelectorAll(".symptom-card")
      .forEach((card) => card.classList.remove("disabled-symptom"));
    updateSelected();
  });
  updateVisibility();
  updateSelected();
}
