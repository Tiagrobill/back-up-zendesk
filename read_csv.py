import pandas as pd
import psycopg2
import os

# Tenta estabelecer a conexão com o banco de dados
try:
    conn = psycopg2.connect(
        host="ep-dry-dawn-a5k50ozh.us-east-2.aws.neon.tech",
        dbname="tickets_zendesk",
        user="tickets_zendesk_owner",
        password="ISyDqw4GxaV3",
        port="5432",
        sslmode="require"
    )
    cursor = conn.cursor()
    print("Conexão bem-sucedida!")
except Exception as e:
    print("Erro ao conectar ao banco de dados:", e)
    conn = None

# Se a conexão foi bem-sucedida, prossiga com a leitura e inserção de dados
if conn:
    # Carrega o CSV com a codificação correta
    try:
        df = pd.read_csv("./comments.csv", encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv("./comments.csv", encoding='latin-1')

    # Exibe as colunas do DataFrame
    print("Colunas no DataFrame:", df.columns)

    # Truncar a tabela antes da inserção
    try:
        cursor.execute("TRUNCATE TABLE tickets;")  # Limpa a tabela
        print("Tabela 'tickets' truncada com sucesso!")
    except Exception as e:
        print("Erro ao truncar a tabela:", e)

    total_rows = len(df)  # Total de registros
    success_count = 0  # Contador de registros inseridos
    erros = []  # Lista para armazenar erros

    # Função para verificar se o arquivo é uma imagem
    def is_image_file(filename):
        valid_extensions = {".jpg", ".jpeg", ".png"}
        return os.path.splitext(filename)[1].lower() in valid_extensions

    # Inserir os dados
    for index, row in df.iterrows():
        ticket_id = row["ticket_id"]
        chat_content = row.get("comment")  # Conteúdo do comentário

        # Caminho da imagem correspondente ao ticket (se existir)
        image_path = f"./downloads/{ticket_id}.jpg"  # Ajuste conforme seu padrão de imagem

        try:
            # Verifique se a imagem existe e é de um tipo válido
            if os.path.exists(image_path) and is_image_file(image_path):
                cursor.execute(
                    "INSERT INTO tickets (ticket_id, chat_content, image_path) VALUES (%s, %s, %s)",
                    (ticket_id, chat_content, image_path)
                )
            else:
                cursor.execute(
                    "INSERT INTO tickets (ticket_id, chat_content, image_path) VALUES (%s, %s, NULL)",
                    (ticket_id, chat_content)
                )
            success_count += 1  # Incrementa o contador de sucesso

        except Exception as e:
            erros.append(f"Erro ao inserir ticket_id {ticket_id}: {e}")

        # Exibe a porcentagem de conclusão no console
        if (index + 1) % 100 == 0 or index + 1 == total_rows:
            percent_complete = (index + 1) / total_rows * 100
            print(f"Progresso: {percent_complete:.2f}% - Inseridos {success_count} registros.")

    # Confirma as mudanças e fecha a conexão
    conn.commit()
    print("Inserção concluída com sucesso!")
    if erros:
        print("Erros encontrados:")
        for erro in erros:
            print(erro)

    cursor.close()
    conn.close()
else:
    print("A conexão com o banco de dados falhou. Verifique suas credenciais e tente novamente.")
