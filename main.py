import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import operacoes


class SistemaEstoque:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Estoque - Loja")
        self.root.geometry("800x500")

        frame_botoes = tk.Frame(root, bg="#2c3e50", width=200)
        frame_botoes.pack(side=tk.LEFT, fill=tk.Y)

        self.frame_tabela = tk.Frame(root)
        self.frame_tabela.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- NOVO: ESTILO VISUAL DA TABELA ---
        estilo = ttk.Style()
        estilo.theme_use("clam")  # Muda o tema padrão para um mais moderno e plano

        # Configura as linhas da tabela
        estilo.configure("Treeview",
                         background="#ffffff",
                         foreground="black",
                         rowheight=30,  # Deixa as linhas mais altas para "respirar"
                         fieldbackground="#ffffff",
                         font=("Arial", 10)
                         )

        # Configura o cabeçalho
        estilo.configure("Treeview.Heading",
                         font=("Arial", 10, "bold"),
                         background="#ecf0f1",  # Fundo cinza claro
                         foreground="#2c3e50",  # Texto escuro
                         relief="flat"  # Remove a borda grossa padrão
                         )

        # Cor de destaque quando o usuário clica numa linha
        estilo.map("Treeview", background=[("selected", "#3498db")])

        # Cria a tabela
        self.tree = ttk.Treeview(self.frame_tabela, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Define as cores para o efeito "Zebrado"
        self.tree.tag_configure("linha_par", background="#f9f9f9")  # Cinza super claro
        self.tree.tag_configure("linha_impar", background="#ffffff")  # Branco


        tk.Button(frame_botoes, text="🔄 Ver Estoque", command=self.ver_estoque, height=2).pack(fill=tk.X, padx=10,
                                                                                               pady=10)
        tk.Button(frame_botoes, text="💰 Registrar Venda", command=self.janela_registrar_venda, height=2).pack(fill=tk.X,
                                                                                                              padx=10,
                                                                                                              pady=5)
        # Botão atualizado para chamar a nova janela customizada
        tk.Button(frame_botoes, text="📦 Entrada de Estoque", command=self.janela_entrada_estoque, height=2).pack(
            fill=tk.X, padx=10, pady=5)

        tk.Button(frame_botoes, text="➕ Novo Produto", command=self.janela_cadastrar_produto, height=2).pack(fill=tk.X,
                                                                                                             padx=10,
                                                                                                             pady=5)
        tk.Button(frame_botoes, text="📜 Histórico de Vendas", command=self.ver_historico, height=2).pack(fill=tk.X,
                                                                                                         padx=10,
                                                                                                         pady=5)
        tk.Button(frame_botoes, text="❌ Excluir Produto", command=self.excluir_produto, bg="#e74c3c", fg="white",
                  height=2).pack(fill=tk.X, padx=10, pady=30)

        # --- CONFIGURANDO OS ATALHOS DO TECLADO ---
        # Usamos lambda e: para ignorar o parâmetro de evento que o teclado envia e apenas chamar a nossa função
        self.root.bind("<F1>", lambda e: self.ver_estoque())
        self.root.bind("<F2>", lambda e: self.janela_registrar_venda())
        self.root.bind("<F3>", lambda e: self.janela_entrada_estoque())
        self.root.bind("<F4>", lambda e: self.janela_cadastrar_produto())
        self.root.bind("<F5>", lambda e: self.ver_historico())
        # Opcional: Se quiser colocar F12 para excluir (para evitar toques acidentais, usei F12 em vez de F6)
        self.root.bind("<F12>", lambda e: self.excluir_produto())

        self.ver_estoque()

    def limpar_tabela(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def configurar_colunas(self, colunas):
        self.tree["columns"] = colunas
        for col in colunas:
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar_coluna(c, False))
            if col.startswith("ID"):
                self.tree.column(col, width=50, anchor=tk.CENTER)
            else:
                self.tree.column(col, width=150)

    def ver_estoque(self):
        self.limpar_tabela()
        # Removi o CodigoBarras daqui temporariamente apenas se você não o usa no SQL, ajuste se necessário.
        self.configurar_colunas(("ID", "Categoria", "Produto", "Tamanho", "Qtd"))
        try:
            dados = operacoes.obter_estoque()
            for index, linha in enumerate(dados):
                # Se o índice for divisível por 2 (par), aplica a tag par, senão, ímpar
                tag = "linha_par" if index % 2 == 0 else "linha_impar"
                self.tree.insert("", tk.END, values=linha, tags=(tag,))
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def ver_historico(self):
        self.limpar_tabela()
        self.configurar_colunas(("ID Produto", "Produto", "Tamanho", "Qtd Vendida", "Data"))
        try:
            dados = operacoes.obter_historico()
            for index, linha in enumerate(dados):
                tag = "linha_par" if index % 2 == 0 else "linha_impar"
                self.tree.insert("", tk.END, values=linha, tags=(tag,))
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def janela_registrar_venda(self):
        janela = tk.Toplevel(self.root)
        janela.title("Registrar Venda")
        janela.geometry("350x350")
        janela.grab_set()

        # --- NOVOS ATALHOS ---
        janela.bind("<Escape>", lambda e: janela.destroy()) # Esc fecha a janela
        janela.bind("<Return>", lambda e: confirmar_venda()) # Enter confirma a venda

        tk.Label(janela, text="ID do Produto:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        entrada_id = tk.Entry(janela, font=("Arial", 12), justify="center")
        entrada_id.pack(pady=5)
        entrada_id.focus_set() # Já abre com o cursor no ID

        lbl_nome_produto = tk.Label(janela, text="Digite o ID...", fg="gray", font=("Arial", 11, "italic"))
        lbl_nome_produto.pack(pady=5)

        def buscar_nome(event):
            texto = entrada_id.get()
            if texto.isdigit():
                nome = operacoes.obter_nome_produto(int(texto))
                if nome:
                    lbl_nome_produto.config(text=f"✅ {nome}", fg="green", font=("Arial", 11, "bold"))
                else:
                    lbl_nome_produto.config(text="❌ Produto não encontrado", fg="red", font=("Arial", 11, "bold"))

        entrada_id.bind("<KeyRelease>", buscar_nome)

        tk.Label(janela, text="Tamanho (P, M, G, etc.):").pack(pady=(10, 5))
        entrada_tam = tk.Entry(janela, justify="center")
        entrada_tam.pack(pady=5)

        tk.Label(janela, text="Quantidade Vendida:").pack(pady=(10, 5))
        entrada_qtd = tk.Entry(janela, justify="center")
        entrada_qtd.pack(pady=5)


        def confirmar_venda():
            try:
                pid = int(entrada_id.get())
                tam = entrada_tam.get()
                qtd = int(entrada_qtd.get())
                if not tam:
                    messagebox.showwarning("Aviso", "Preencha o tamanho!")
                    return
                operacoes.registrar_venda_db(pid, tam, qtd)
                messagebox.showinfo("Sucesso", "Venda registrada!")
                janela.destroy()
                self.ver_estoque()
            except Exception:
                messagebox.showerror("Erro", "Verifique os dados ou o estoque.")

        tk.Button(janela, text="Confirmar Venda [Enter]", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=confirmar_venda, height=2).pack(pady=20, fill=tk.X, padx=50)

    def ordenar_coluna(self, coluna, reverso):
        # Pega todos os valores da coluna clicada e os IDs das linhas correspondentes
        dados = [(self.tree.set(k, coluna), k) for k in self.tree.get_children('')]
        
        # Tenta ordenar como número (para ID e Qtd não ficarem assim: 1, 10, 2, 3...)
        try:
            dados.sort(key=lambda t: int(t[0]), reverse=reverso)
        except ValueError:
            # Se der erro (porque é texto como Nome ou Categoria), ordena como texto normal
            dados.sort(reverse=reverso)

        # Reorganiza as linhas na tabela visualmente
        for index, (valor, k) in enumerate(dados):
            self.tree.move(k, '', index)

        # Atualiza o cabeçalho para que o próximo clique inverta a ordem (crescente <-> decrescente)
        self.tree.heading(coluna, command=lambda: self.ordenar_coluna(coluna, not reverso))

    def janela_entrada_estoque(self):
        # Nova janela com o mesmo sistema de busca de nome
        janela = tk.Toplevel(self.root)
        janela.title("Entrada de Estoque (Reposição)")
        janela.geometry("350x350")
        janela.grab_set()

        janela.bind("<Escape>", lambda e: janela.destroy())
        janela.bind("<Return>", lambda e: confirmar_entrada())

        tk.Label(janela, text="ID do Produto:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        entrada_id = tk.Entry(janela, font=("Arial", 12), justify="center")
        entrada_id.pack(pady=5)
        entrada_id.focus_set()

        lbl_nome_produto = tk.Label(janela, text="Digite o ID...", fg="gray", font=("Arial", 11, "italic"))
        lbl_nome_produto.pack(pady=5)

        def buscar_nome(event):
            texto = entrada_id.get()
            if texto.isdigit():
                nome = operacoes.obter_nome_produto(int(texto))
                if nome:
                    lbl_nome_produto.config(text=f"✅ {nome}", fg="green", font=("Arial", 11, "bold"))
                else:
                    lbl_nome_produto.config(text="❌ Produto não encontrado", fg="red", font=("Arial", 11, "bold"))
            else:
                lbl_nome_produto.config(text="Digite o ID...", fg="gray", font=("Arial", 11, "italic"))

        entrada_id.bind("<KeyRelease>", buscar_nome)

        tk.Label(janela, text="Tamanho (P, M, G, etc.):").pack(pady=(10, 5))
        entrada_tam = tk.Entry(janela, justify="center")
        entrada_tam.pack(pady=5)

        tk.Label(janela, text="Quantidade (Que Chegou):").pack(pady=(10, 5))
        entrada_qtd = tk.Entry(janela, justify="center")
        entrada_qtd.pack(pady=5)

        def confirmar_entrada():
            try:
                pid = int(entrada_id.get())
                tam = entrada_tam.get()
                qtd = int(entrada_qtd.get())

                if not tam:
                    messagebox.showwarning("Aviso", "Preencha o tamanho!")
                    return

                operacoes.registrar_entrada_db(pid, tam, qtd)
                messagebox.showinfo("Sucesso", "Estoque atualizado!")
                janela.destroy()
                self.ver_estoque()
            except ValueError:
                messagebox.showerror("Erro", "Verifique os números digitados.")
            except Exception as e:
                messagebox.showerror("Erro do Banco", str(e))

        tk.Button(janela, text="Confirmar Entrada", bg="#2980b9", fg="white", font=("Arial", 10, "bold"),
                  command=confirmar_entrada, height=2).pack(pady=20, fill=tk.X, padx=50)

    def janela_cadastrar_produto(self):
        janela = tk.Toplevel(self.root)
        janela.title("Cadastrar Novo Produto")
        janela.geometry("350x300")
        janela.grab_set()

        janela.bind("<Escape>", lambda e: janela.destroy())
        janela.bind("<Return>", lambda e: confirmar_cadastro())

        tk.Label(janela, text="ID da Categoria:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        entrada_cat = tk.Entry(janela, font=("Arial", 12), justify="center")
        entrada_cat.pack(pady=5)
        entrada_cat.focus_set()

        lbl_nome_categoria = tk.Label(janela, text="Digite o ID (Ex: 1, 2, 3...)", fg="gray",
                                      font=("Arial", 11, "italic"))
        lbl_nome_categoria.pack(pady=5)

        def buscar_categoria(event):
            texto = entrada_cat.get()
            if texto.isdigit():
                nome = operacoes.obter_nome_categoria(int(texto))
                if nome:
                    lbl_nome_categoria.config(text=f"✅ Categoria: {nome}", fg="green", font=("Arial", 11, "bold"))
                else:
                    lbl_nome_categoria.config(text="❌ Categoria não encontrada", fg="red", font=("Arial", 11, "bold"))
            else:
                lbl_nome_categoria.config(text="Digite o ID (Ex: 1, 2, 3...)", fg="gray", font=("Arial", 11, "italic"))

        entrada_cat.bind("<KeyRelease>", buscar_categoria)

        tk.Label(janela, text="Nome do Produto:").pack(pady=(10, 5))
        entrada_nome = tk.Entry(janela, justify="center", width=25)
        entrada_nome.pack(pady=5)

        def confirmar_cadastro():
            try:
                cid = int(entrada_cat.get())
                nome_prod = entrada_nome.get()

                if not nome_prod:
                    messagebox.showwarning("Aviso", "Preencha o nome do produto!")
                    return

                novo_id = operacoes.cadastrar_produto_db(cid, nome_prod)
                messagebox.showinfo("Sucesso", f"Produto cadastrado!\nO ID dele é: {novo_id}")
                janela.destroy()
                self.ver_estoque()
            except ValueError:
                messagebox.showerror("Erro", "Verifique o ID da categoria digitado.")
            except Exception as e:
                messagebox.showerror("Erro do Banco", str(e))

        tk.Button(janela, text="Confirmar Cadastro", bg="#8e44ad", fg="white", font=("Arial", 10, "bold"),
                  command=confirmar_cadastro, height=2).pack(pady=20, fill=tk.X, padx=50)

    def excluir_produto(self):
        prod_id = simpledialog.askinteger("Excluir", "Digite o ID do Produto para excluir definitivamente:")
        if not prod_id: return

        if not messagebox.askyesno("Atenção", "Tem certeza? Isso apagará o produto do estoque também."): return

        try:
            operacoes.excluir_produto_db(prod_id)
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            self.ver_estoque()
        except Exception as e:
            messagebox.showerror("Erro", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaEstoque(root)
    root.mainloop()