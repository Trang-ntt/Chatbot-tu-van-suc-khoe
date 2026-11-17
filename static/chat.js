let sessionId = null;
const $ = (id) => document.getElementById(id);
function addBubble(text, who = "bot") {
  const el = document.createElement("div");
  el.className = "bubble " + who;
  el.textContent = text;
  $("messages").appendChild(el);
  $("messages").scrollTop = $("messages").scrollHeight;
  return el;
}
async function post(url, data) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const raw = await r.text();
  let d;
  try {
    d = JSON.parse(raw);
  } catch {
    throw new Error(
      `Máy chủ trả về nội dung không phải JSON (HTTP ${r.status}). Hãy xem cửa sổ Terminal để tìm lỗi Python.`,
    );
  }
  if (!r.ok) throw new Error(d.loi || `Yêu cầu thất bại (HTTP ${r.status})`);
  return d;
}
function showResult(d) {
  const box = document.createElement("div");
  box.className = "bubble bot";
  if (d.canh_bao) {
    const warn = document.createElement("div");
    warn.className = "warning";
    warn.textContent =
      "⚠ Có dấu hiệu cảnh báo. Hãy tìm trợ giúp y tế khẩn cấp.";
    box.appendChild(warn);
  }
  const summary = document.createElement("p");
  summary.textContent =
    "Triệu chứng ghi nhận: " + (d.trieu_chung_co.join(", ") || "Chưa có");
  box.appendChild(summary);
  if (d.trieu_chung_khong.length) {
    const neg = document.createElement("p");
    neg.textContent = "Không có: " + d.trieu_chung_khong.join(", ");
    box.appendChild(neg);
  }
  const result = document.createElement("div");
  result.className = "result";
  const heading = document.createElement("h3");
  heading.textContent = "Các bệnh có biểu hiện tương tự trong dữ liệu";
  result.appendChild(heading);
  for (const x of d.danh_sach_benh) {
    const row = document.createElement("div");
    row.className = "disease";
    const name = document.createElement("b");
    name.textContent = x.ten;
    const score = document.createElement("span");
    score.className = "score";
    score.textContent = x.diem.toFixed(2) + "%";
    row.append(name, score);
    result.appendChild(row);
  }
  box.appendChild(result);
  const advice = document.createElement("p");
  advice.textContent = d.loi_khuyen;
  box.appendChild(advice);
  $("messages").appendChild(box);
  $("messages").scrollTop = $("messages").scrollHeight;
}
function handle(d) {
  if (d.loai === "cau_hoi" || d.loai === "chua_hieu") addBubble(d.tin_nhan);
  else if (d.loai === "ket_qua") showResult(d);
}
$("start").onclick = async () => {
  try {
    const d = await post("/api/bat-dau", {
      tuoi: $("age").value,
      gioi: $("sex").value,
    });
    sessionId = d.ma_phien;
    $("setup").classList.add("hidden");
    $("chat").classList.remove("hidden");
    $("messages").innerHTML = "";
    addBubble(d.tin_nhan);
  } catch (e) {
    $("setupError").textContent = e.message;
  }
};
$("chatForm").onsubmit = async (e) => {
  e.preventDefault();
  const text = $("message").value.trim();
  if (!text) return;
  $("message").value = "";
  addBubble(text, "user");
  try {
    handle(
      await post("/api/tin-nhan", { ma_phien: sessionId, noi_dung: text }),
    );
  } catch (err) {
    addBubble(err.message);
  }
};
$("reset").onclick = async () => {
  if (sessionId)
    try {
      await post("/api/lam-moi", { ma_phien: sessionId });
    } catch {}
  sessionId = null;
  $("chat").classList.add("hidden");
  $("setup").classList.remove("hidden");
  $("messages").innerHTML = "";
  $("setupError").textContent = "";
};
