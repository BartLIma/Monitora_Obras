import pandas as pd
import streamlit as st
import os
import urllib.parse

st.title("🏗️ Monitoramento de Obras — Novo PAC & Retomada")

# --- CARREGAMENTO DO BANCO DE SECRETÁRIOS (COSEMS/PB) ---
df_sec = pd.DataFrame()
if os.path.exists("secretarios_cosems_pb.csv"):
    for enc in ["utf-8-sig", "latin1", "cp1252"]:
        try:
            df_sec = pd.read_csv("secretarios_cosems_pb.csv", sep=";", dtype=str)
            df_sec.columns = df_sec.columns.str.strip()
            for col in df_sec.columns:
                df_sec[col] = df_sec[col].fillna("").astype(str).str.strip()
            break
        except Exception:
            continue

# --- MENU PRINCIPAL: SELEÇÃO DO TIPO DE ACOMPANHAMENTO ---
st.markdown("### 🎛️ Escopo do Monitoramento")
tipo_acompanhamento = st.radio(
    "Selecione o programa de execução:",
    ["Obras Novo PAC", "Retomada de Obras Paralisadas"],
    horizontal=True
)

st.markdown("---")

obras_filtradas = pd.DataFrame()
muni = ""
uf = "PB"
prop_escolhida = ""
msg_contexto = ""
programa_nome = ""

# =========================================================================
# FLUXO 1: OBRAS NOVO PAC
# =========================================================================
if tipo_acompanhamento == "Obras Novo PAC":
    st.subheader("⚡ Painel de Controle — Novo PAC")
    arquivo_pac = "PB - Lima(PAC_PB).csv"
    
    try:
        df_pac = pd.read_csv(arquivo_pac, sep=";", encoding="utf-8-sig", dtype=str)
    except Exception:
        try:
            df_pac = pd.read_csv(arquivo_pac, sep=";", encoding="latin1", dtype=str)
        except Exception:
            st.error(f"⚠️ Arquivo '{arquivo_pac}' não localizado na pasta do projeto.")
            st.stop()

    df_pac.columns = df_pac.columns.str.strip()
    for col in df_pac.columns:
        df_pac[col] = df_pac[col].fillna("").astype(str).str.strip()

    metodo_busca = st.radio("Buscar por:", ["Município (PAC)", "Proposta (PAC)"], horizontal=True, key="busca_pac")

    if "Município" in metodo_busca:
        busca_muni = st.text_input("Digite o nome do Município:", key="muni_pac")
        if busca_muni.strip():
            obras_filtradas = df_pac[df_pac["Município"].str.lower().str.contains(busca_muni.lower().strip(), na=False)]
    else:
        busca_prop = st.text_input("Digite o número exato da Proposta:", key="prop_pac")
        if busca_prop.strip():
            obras_filtradas = df_pac[df_pac["Proposta"] == busca_prop.strip()]

       if not obras_filtradas.empty:
        opcoes_obras = [f"{row['Proposta']} - {row.get('Nome da unidade', 'Obra')} ({row.get('Componente', 'PAC')})" for idx, row in obras_filtradas.iterrows()]
        obra_selecionada = st.selectbox("Selecione a obra do PAC:", opcoes_obras, key="sel_pac")
        
        # CORREÇÃO: Captura apenas o número da proposta (primeiro item da divisão)
        prop_escolhida = obra_selecionada.split(" - ")[0].strip()
        
        # CORREÇÃO: Usa .iloc[0] para extrair a linha como um dicionário/série único
        dados_obra = obras_filtradas[obras_filtradas["Proposta"] == prop_escolhida].iloc[0]
        
        muni = dados_obra.get("Município", "").upper()
        uf = dados_obra.get("UF", "PB").upper()
        unidade = dados_obra.get("Nome da unidade", "")
        comp = dados_obra.get("Componente", "")
        sit_sismob = dados_obra.get("Situação no SISMOB", "")
        exec_fisica = dados_obra.get("Execução física (%) SISMOB", "")
        dias_sem_mon = dados_obra.get("Dias sem monitoramento SISMOB", "")
        sit_pac = dados_obra.get("Situação equipe PAC", "")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Proposta:** {prop_escolhida} | **UF:** {uf}")
            st.markdown(f"**Município:** {muni}")
            st.markdown(f"**Unidade:** {unidade}")
            st.markdown(f"**Componente:** {comp}")
        with col2:
            st.markdown(f"**Situação SISMOB:** {sit_sismob}")
            st.markdown(f"**Execução Física:** {exec_fisica}%")
            st.markdown(f"**Dias Sem Monit.:** {dias_sem_mon} dias")
            st.markdown(f"**Status Equipe PAC:** {sit_pac}")

        msg_contexto = f"• Unidade: {unidade}\n• Componente: {comp}\n• Situação SISMOB: {sit_sismob}\n• Execução Física: {exec_fisica}%\n• Dias Sem Monitoramento: {dias_sem_mon}\n• Status PAC: {sit_pac}"
        programa_nome = "Obras Novo PAC"
# =========================================================================
# FLUXO 2: RETOMADA DE OBRAS PARALISADAS (COLUNAS REAIS)
# =========================================================================
else:
    st.subheader("🔄 Painel de Controle — Retomada de Obras")
    arquivo_retomada = "PB - Lima(RetomadaObras).csv"
    
    try:
        df_ret = pd.read_csv(arquivo_retomada, sep=";", encoding="utf-8-sig", dtype=str)
    except Exception:
        try:
            df_ret = pd.read_csv(arquivo_retomada, sep=";", encoding="latin1", dtype=str)
        except Exception:
            st.error(f"⚠️ Arquivo '{arquivo_retomada}' não localizado na pasta do projeto.")
            st.stop()

    df_ret.columns = df_ret.columns.str.strip()
    for col in df_ret.columns:
        df_ret[col] = df_ret[col].fillna("").astype(str).str.strip()

    metodo_busca = st.radio("Buscar por:", ["Município (Retomada)", "Proposta (Retomada)"], horizontal=True, key="busca_ret")

    if "Município" in metodo_busca:
        busca_muni = st.text_input("Digite o nome do Município:", key="muni_ret")
        if busca_muni.strip():
            obras_filtradas = df_ret[df_ret["Município"].str.lower().str.contains(busca_muni.lower().strip(), na=False)]
    else:
        busca_prop = st.text_input("Digite o número exato da Proposta:", key="prop_ret")
        if busca_prop.strip():
            obras_filtradas = df_ret[df_ret["Proposta"] == busca_prop.strip()]

       if not obras_filtradas.empty:
        opcoes_obras = [f"{row[col_prop_ret]} - {row.get('Nome da unidade', 'Obra')} ({row.get('Componente', 'Retomada')})" for idx, row in obras_filtradas.iterrows()]
        obra_selecionada = st.selectbox("Selecione a obra para detalhar:", opcoes_obras, key="sel_ret")
        
        # CORREÇÃO: Captura apenas o número da proposta (primeiro item da divisão)
        prop_escolhida = obra_selecionada.split(" - ")[0].strip()
        
        # CORREÇÃO: Usa .iloc[0] para extrair a linha como um dicionário/série único
        dados_obra = obras_filtradas[obras_filtradas[col_prop_ret] == prop_escolhida].iloc[0]
        
        muni = dados_obra.get(col_muni_ret, "").upper()
        uf = dados_obra.get("UF", "PB").upper()
        unidade = dados_obra.get("Nome da unidade", "")
        comp = dados_obra.get("Componente", "")
        porte = dados_obra.get("Porte", "")
        modalidade = dados_obra.get("Modalidade", "")
        sit_sismob = dados_obra.get("Situação no SISMOB", "")
        exec_fisica = dados_obra.get("Execução física (%) SISMOB", "")
        dias_sem_mon = dados_obra.get("Dias sem monitoramento SISMOB", "")
        prioridade = dados_obra.get("Prioridade de contato", "")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown(f"**Proposta:** {prop_escolhida} | **UF:** {uf}")
            st.markdown(f"**Município:** {muni}")
            st.markdown(f"**Unidade:** {unidade}")
            st.markdown(f"**Componente:** {comp}")
            st.markdown(f"**Porte / Modalidade:** {porte} | {modalidade}")
        with col_r2:
            st.markdown(f"**Situação SISMOB:** {sit_sismob}")
            st.markdown(f"**Execução Física:** {exec_fisica}%")
            st.markdown(f"**Dias Sem Monit.:** {dias_sem_mon} dias")
            st.markdown(f"**Prioridade de Contato:** `{prioridade}`")
        
        msg_contexto = f"• Unidade: {unidade}\n• Componente: {comp}\n• Situação SISMOB: {sit_sismob}\n• Execução Física: {exec_fisica}%\n• Dias Sem Monitoramento: {dias_sem_mon}\n• Prioridade: {prioridade}"
        programa_nome = "Retomada de Obras Paralisadas"
# =========================================================================
# BLOCO INTEGRADO: SECRETÁRIOS (COSEMS/PB) + WHATSAPP (VERSÕES 2, 3 e 4)
# =========================================================================
if not obras_filtradas.empty and muni:
    st.markdown("---")
    st.subheader("📋 Dados de Contato do Gestor Local")

    nome_secretario = "Não localizado no cadastro"
    fone_secretario = ""
    
    if not df_sec.empty:
        col_muni_sec = "Município" if "Município" in df_sec.columns else df_sec.columns
        
        col_nome_sec = [c for c in df_sec.columns if "nome" in c.lower() or "secretario" in c.lower()]
        col_nome_sec = col_nome_sec if col_nome_sec else df_sec.columns
        
        col_fone_sec = [c for c in df_sec.columns if "tel" in c.lower() or "cel" in c.lower() or "fone" in c.lower() or "whatsapp" in c.lower()]
        col_fone_sec = col_fone_sec if col_fone_sec else df_sec.columns
        
        filtro_sec = df_sec[df_sec[col_muni_sec].str.lower().str.strip() == muni.lower().strip()]
        if not filtro_sec.empty:
            nome_secretario = filtro_sec.iloc.get(col_nome_sec, "Não Informado")
            fone_secretario = filtro_sec.iloc.get(col_fone_sec, "")

    st.write(f"**Secretário(a) de Saúde:** {nome_secretario}")
    st.write(f"**WhatsApp/Telefone:** {fone_secretario if fone_secretario else 'Não informado'}")

    saudacao = "Prezado(a) Secretário(a)" if "Não localizado" in nome_secretario else f"Prezado(a) Secretário(a) {nome_secretario}"
    
    mensagem_whatsapp = (
        f"{saudacao},\n\n"
        f"Entramos em contato para verificar a evolução técnica e pendências de engenharia em seu município, vinculadas ao programa de {programa_nome}:\n\n"
        f"📌 *DADOS DO INSTRUMENTO:*\n"
        f"• Município: {muni} - {uf}\n"
        f"• Proposta Nº: {prop_escolhida}\n"
        f"{msg_contexto}\n\n"
        f"Solicitamos atenção especial quanto ao andamento dos trâmites administrativos para a regularização do objeto. "
        f"Permanecemos à disposição para suporte técnico."
    )
    
    st.text_area("Visualização da Mensagem:", value=mensagem_whatsapp, height=220)
    
    # Botão de Ação Rápida WhatsApp
    if fone_secretario:
        num_limpo = "".join(filter(str.isdigit, fone_secretario))
        if len(num_limpo) <= 11 and num_limpo != "":
            num_limpo = f"55{num_limpo}"
            
        texto_url = urllib.parse.quote(mensagem_whatsapp)
        link_api = f"https://whatsapp.com{num_limpo}&text={texto_url}"
        
        st.markdown(f"[📲 Enviar Diretamente via WhatsApp Web]({link_api})")
    
    st.markdown("**Se preferir copiar manualmente, clique no ícone no canto superior direito do bloco abaixo:**")
    st.code(mensagem_whatsapp, language="text")

# Rodapé Técnico do Corecon
st.markdown("---")
st.markdown("<p style='text-align:right; font-size:12px; color:gray;'>Bartolomeu Lima - Corecon-ES 1541</p>", unsafe_allow_html=True)
