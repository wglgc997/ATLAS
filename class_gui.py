# import csv
# import tkinter as tk
# from tkinter import ttk, messagebox, filedialog
# from urllib.parse import urljoin, urlparse
# import threading
# import concurrent.futures
# from functions import fetch_html, extract_links, check_link
#
#
# class LinkCheckerApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Verificador de Links Quebrados")
#         self.root.geometry("900x600")
#         try:
#             self.root.iconbitmap("icon.ico")
#         except Exception:
#             pass
#
#         self.results = []  # guarda resultados p/ exportar
#
#         # Top frame: URL + controles
#         top = ttk.Frame(root, padding=10)
#         top.pack(fill="x")
#
#         ttk.Label(top, text="URL:").pack(side="left")
#         self.url_var = tk.StringVar(value="https://www.eddymens.com/blog/page-with-broken-pages-for-testing-53049e870421")
#         self.url_entry = ttk.Entry(top, textvariable=self.url_var, width=80)
#         self.url_entry.pack(side="left", padx=6)
#
#         self.threads_var = tk.IntVar(value=20)
#         ttk.Label(top, text="Threads:").pack(side="left", padx=(10,2))
#         self.threads_spin = ttk.Spinbox(top, from_=5, to=50, textvariable=self.threads_var, width=4)
#         self.threads_spin.pack(side="left")
#
#         self.timeout_var = tk.IntVar(value=10)
#         ttk.Label(top, text="Timeout (s):").pack(side="left", padx=(10,2))
#         self.timeout_spin = ttk.Spinbox(top, from_=3, to=30, textvariable=self.timeout_var, width=4)
#         self.timeout_spin.pack(side="left")
#
#         self.run_btn = ttk.Button(top, text="Analisar", command=self.on_run)
#         self.run_btn.pack(side="left", padx=10)
#
#         self.save_btn = ttk.Button(top, text="Salvar CSV", command=self.save_csv, state="disabled")
#         self.save_btn.pack(side="left")
#
#         # Treeview (tabela)
#         columns = ("texto", "url_encontrada", "url_absoluta", "status", "ok", "redir", "url_final", "metodo", "erro")
#         self.tree = ttk.Treeview(root, columns=columns, show="headings")
#         for col, title, width in [
#             ("texto", "Texto", 140),
#             ("url_encontrada", "URL Encontrada", 180),
#             ("url_absoluta", "URL Absoluta", 220),
#             ("status", "Status", 60),
#             ("ok", "OK", 40),
#             ("redir", "Redirecionou", 90),
#             ("url_final", "URL Final", 220),
#             ("metodo", "Método", 70),
#             ("erro", "Erro", 160),
#         ]:
#             self.tree.heading(col, text=title)
#             self.tree.column(col, width=width, anchor="w")
#         self.tree.pack(fill="both", expand=True, padx=10, pady=10)
#
#         # Barra de status
#         self.status_var = tk.StringVar(value="Pronto")
#         status = ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w")
#         status.pack(fill="x", side="bottom")
#
#     def set_busy(self, busy: bool):
#         self.run_btn.config(state=("disabled" if busy else "normal"))
#         self.save_btn.config(state=("disabled" if busy else ("normal" if self.results else "disabled")))
#         self.url_entry.config(state=("disabled" if busy else "normal"))
#         self.threads_spin.config(state=("disabled" if busy else "normal"))
#         self.timeout_spin.config(state=("disabled" if busy else "normal"))
#         self.root.config(cursor="watch" if busy else "")
#
#     def on_run(self):
#         url = self.url_var.get().strip()
#         if not url or not urlparse(url).scheme:
#             messagebox.showerror("Erro", "Informe uma URL válida (ex: https://site.com).")
#             return
#         self.results.clear()
#         for item in self.tree.get_children():
#             self.tree.delete(item)
#         self.set_busy(True)
#         self.status_var.set("Baixando HTML e extraindo links...")
#
#         t = threading.Thread(target=self.run_check, args=(url, self.threads_var.get(), self.timeout_var.get()), daemon=True)
#         t.start()
#
#     def run_check(self, url: str, max_workers: int, timeout: int):
#         try:
#             html = fetch_html(url)
#             if not html:
#                 self._ui_error("Não foi possível carregar a página (GET falhou).")
#                 return
#             links = extract_links(url, html)
#             total = len(links)
#             self._ui_status(f"{total} links encontrados. Verificando...")
#
#             results = []
#             done_count = 0
#             with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
#                 futures = {ex.submit(check_link, it["abs_url"], timeout): it for it in links}
#                 for fut in concurrent.futures.as_completed(futures):
#                     it = futures[fut]
#                     r = fut.result()
#                     row = {
#                         "Texto do Link": it["text"],
#                         "URL Encontrada": it["href"],
#                         "URL Absoluta": r["url"],
#                         "Status": r["status_code"],
#                         "OK": r["ok"],
#                         "Redirecionou?": r["redirected"],
#                         "URL Final": r["final_url"],
#                         "Método": r["method_used"],
#                         "Erro": r["error"],
#                     }
#                     results.append(row)
#                     done_count += 1
#                     if done_count % 5 == 0 or done_count == total:
#                         self._ui_status(f"Verificando... {done_count}/{total}")
#
#             # atualizar UI
#             self.results = results
#             self._ui_fill_table(results)
#             broken = [x for x in results if (not x["OK"]) or x["Erro"]]
#             self._ui_status(f"Concluído. Links com problema: {len(broken)} / {len(results)}")
#             self._ui_enable_save()
#         except Exception as e:
#             self._ui_error(f"Erro: {e}")
#
#     # --- métodos para agendar na thread da UI ---
#     def _ui_status(self, text):
#         self.root.after(0, lambda: self.status_var.set(text))
#
#     def _ui_error(self, msg):
#         def f():
#             self.set_busy(False)
#             self.status_var.set("Erro")
#             messagebox.showerror("Erro", msg)
#         self.root.after(0, f)
#
#     def _ui_fill_table(self, rows):
#         def f():
#             for row in rows:
#                 self.tree.insert("", "end", values=(
#                     row["Texto do Link"],
#                     row["URL Encontrada"],
#                     row["URL Absoluta"],
#                     row["Status"] if row["Status"] is not None else "-",
#                     "Sim" if row["OK"] else "Não",
#                     "Sim" if row["Redirecionou?"] else "Não",
#                     row["URL Final"] if row["URL Final"] else "-",
#                     row["Método"] if row["Método"] else "-",
#                     row["Erro"] if row["Erro"] else "-"
#                 ))
#             self.set_busy(False)
#         self.root.after(0, f)
#
#     def _ui_enable_save(self):
#         self.root.after(0, lambda: self.save_btn.config(state=("normal" if self.results else "disabled")))
#
#     def save_csv(self):
#         if not self.results:
#             return
#         path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
#         if not path:
#             return
#         try:
#             with open(path, "w", newline="", encoding="utf-8") as f:
#                 writer = csv.DictWriter(f, fieldnames=[
#                     "Texto do Link","URL Encontrada","URL Absoluta","Status","OK",
#                     "Redirecionou?","URL Final","Método","Erro"
#                 ])
#                 writer.writeheader()
#                 for row in self.results:
#                     writer.writerow(row)
#             messagebox.showinfo("OK", f"Relatório salvo em:\n{path}")
#         except Exception as e:
#             messagebox.showerror("Erro", f"Falha ao salvar CSV:\n{e}")