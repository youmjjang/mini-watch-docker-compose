"use client";
import { useState } from "react";
import { requestJson } from "../api/client";

export default function AnalysisClient() {
  const [afterId, setAfterId] = useState(null);
  const [referenceTime, setReferenceTime] = useState(null);
  const [threshold, setThreshold] = useState("10");
  const [card, setCard] = useState(null);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);
  async function start() {
    try {
      const result = await requestJson("/api/analysis/start", "POST");
      setAfterId(result.after_id); setReferenceTime(null); setCard(null); setOpen(false); setError("");
    } catch (e) { setError(e.message); }
  }
  async function load() {
    try {
      const params = new URLSearchParams({ after_id: String(afterId), threshold });
      if (referenceTime) params.set("reference_time", referenceTime);
      const result = await requestJson("/api/analysis?" + params.toString());
      setReferenceTime(result.reference_time); setCard(result.card); setError("");
    } catch (e) { setError(e.message); }
  }
  return <section className="panel">
    <div className="actions"><button onClick={start}>새 관찰 시작</button>
    <label>비교 기준<input type="number" min="1" max="1000000" value={threshold} onChange={e=>setThreshold(e.target.value)} /></label>
    <button disabled={afterId === null || !threshold} onClick={load}>결과 불러오기</button></div>
    {afterId !== null && <p>시작 ID: {afterId} / 기준시각: {referenceTime || "첫 결과를 불러올 때 결정"}</p>}
    {error && <p role="alert" className="error">{error}</p>}
    {card && <article><h3>{card.title}</h3><p>관찰값: <strong>{card.observed}</strong> · 기준: {card.threshold} · 판정: <strong>{card.verdict}</strong></p>
      <p>{card.reason}</p><p>근거 ID: {card.evidence.join(", ") || "없음"}</p>
      <button onClick={()=>setOpen(!open)}>{open ? "근거 닫기" : "근거 보기"} ({card.records.length}행)</button>
      {open && <div style={{overflowX:"auto"}}><table><thead><tr><th>ID</th><th>수신시각</th><th>방법</th><th>경로</th><th>상태</th><th>종류</th></tr></thead>
      <tbody>{card.records.map(r=><tr key={r.id}><td>{r.id}</td><td>{r.occurred_at}</td><td>{r.method}</td><td>{r.path}</td><td>{r.status_code}</td><td>{r.kind}</td></tr>)}</tbody></table></div>}
    </article>}
  </section>;
}
