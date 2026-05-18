import psycopg2
from database import conectar

def obter_estoque():
    conn = conectar()
    cur = conn.cursor()
    # O uso do LEFT JOIN garante que todos os produtos apareçam.
    # O COALESCE coloca um traço '-' no tamanho e '0' na quantidade se o estoque não existir.
    cur.execute("""
        SELECT 
            e.id, 
            c.nome, 
            p.nome, 
            COALESCE(e.tamanho, '-'), 
            COALESCE(e.quantidade, 0)
        FROM produtos p
        JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN estoque e ON p.id = e.produto_id
        ORDER BY p.id ASC, e.tamanho ASC;
    """)
    dados = cur.fetchall()
    conn.close()
    return dados


def obter_historico():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.nome, h.tamanho, h.quantidade_vendida, TO_CHAR(h.data_venda, 'DD/MM/YYYY HH24:MI')
        FROM historico_saidas h
        JOIN produtos p ON h.produto_id = p.id
        ORDER BY h.data_venda DESC LIMIT 50;
    """)
    dados = cur.fetchall()
    conn.close()
    return dados


def obter_nome_produto(prod_id):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("SELECT nome FROM produtos WHERE id = %s", (prod_id,))
        res = cur.fetchone()
        return res[0] if res else None
    except Exception:
        return None
    finally:
        conn.close()

def obter_nome_categoria(cat_id):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("SELECT nome FROM categorias WHERE id = %s", (cat_id,))
        res = cur.fetchone()
        return res[0] if res else None
    except Exception:
        return None
    finally:
        conn.close()


def registrar_venda_db(prod_id, tam, qtd):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("SELECT quantidade FROM estoque WHERE id = %s AND tamanho = %s", (prod_id, tam.upper()))
        res = cur.fetchone()

        if not res or res[0] < qtd:
            raise ValueError("Estoque insuficiente ou produto não encontrado neste tamanho!")

        cur.execute("UPDATE estoque SET quantidade = quantidade - %s WHERE id = %s AND tamanho = %s",
                    (qtd, prod_id, tam.upper()))
        cur.execute("INSERT INTO historico_saidas (produto_id, tamanho, quantidade_vendida) VALUES (%s, %s, %s)",
                    (prod_id, tam.upper(), qtd))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def registrar_entrada_db(prod_id, tam, qtd):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO estoque (produto_id, tamanho, quantidade) VALUES (%s, %s, %s)
            ON CONFLICT (produto_id, tamanho) DO UPDATE SET quantidade = estoque.quantidade + EXCLUDED.quantidade;
        """, (prod_id, tam.upper(), qtd))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def cadastrar_produto_db(cat_id, nome):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO produtos (categoria_id, nome) VALUES (%s, %s) RETURNING id;", (cat_id, nome))
        novo_id = cur.fetchone()[0]
        conn.commit()
        return novo_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def excluir_produto_db(prod_id):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM estoque WHERE produto_id = %s", (prod_id,))
        cur.execute("DELETE FROM produtos WHERE id = %s", (prod_id,))
        conn.commit()
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise ValueError(
            "Você NÃO PODE excluir um produto que já possui histórico de vendas.\nFaça a entrada do estoque com quantidade 0.")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()