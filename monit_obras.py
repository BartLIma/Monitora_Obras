import pandas as pd
import streamlit as st
import os
import urllib.parse

st.set_page_config(layout="wide")

# --- BANCO DE COORDENADAS MESTRE EXPANDIDO DA PARAÍBA ---
coordenadas_pb = {
    "alcantil": [-7.7458, -36.0592], "alhandra": [-7.4393, -34.9136], "arara": [-6.8278, -35.7578], "aroeiras": [-7.4831, -35.7103],
    "barra de santa rosa": [-6.7194, -36.0617], "barra de sao miguel": [-7.7522, -36.3197], "bayeux": [-7.1253, -34.9322], "belem do brejo do cruz": [-6.1856, -37.5342],
    "boqueirao": [-7.4981, -36.1322], "borborema": [-6.8042, -35.6189], "cabaceiras": [-7.4914, -36.2872], "cacimba de dentro": [-6.6436, -35.7836],
    "cajazeiras": [-6.8886, -38.5583], "campina grande": [-7.2247, -35.8772], "conde": [-7.2597, -34.9075], "coremas": [-7.0142, -38.0036],
    "cruz do espirito santo": [-7.1411, -35.0864], "desterro": [-7.2917, -37.3119], "diamante": [-7.3789, -38.1936], "duas estradas": [-6.7144, -35.4528],
    "esperanca": [-7.0253, -35.8578], "frei martinho": [-6.4253, -36.4356], "itabaiana": [-7.3167, -35.3333], "itapororoca": [-6.7917, -35.1517],
    "joao pessoa": [-7.1198, -34.8450], "junco do serido": [-6.9856, -36.7214], "juripiranga": [-7.4042, -35.2558], "mamanguape": [-6.8386, -35.1264],
    "mari": [-7.0583, -35.2217], "mogeiro": [-7.2922, -35.4744], "nova palmeira": [-6.6575, -36.4186], "patos": [-7.0269, -37.2797],
    "paulista": [-6.5925, -37.6247], "pianco": [-7.1983, -37.9286], "pilar": [-7.2686, -35.1217], "pocinhos": [-7.0744, -36.0617],
    "puxinana": [-7.1594, -35.9614], "salgadinho": [-7.1006, -36.8472], "santa luzia": [-6.8722, -36.9181], "santa rita": [-7.1139, -34.9736],
    "sao jose da lagoa tapada": [-6.9458, -38.1636], "sao jose de piranhas": [-7.1167, -38.5022], "sao sebastiao de lagoa de roca": [-7.0631, -35.8456], "serra branca": [-7.4839, -36.6631],
    "solanea": [-6.8447, -35.6925], "sousa": [-6.7611, -38.2250], "teixeira": [-7.2231, -37.2522], "vista serrana": [-6.7381, -37.5614],
    "alagoa grande": [-7.0333, -35.6186], "areial": [-7.0494, -35.9283], "bananeiras": [-6.7547, -35.6339], "bonito de santa fe": [-7.1544, -38.7517],
    "brejo do cruz": [-6.3475, -37.4981], "caapora": [-7.5133, -34.9039], "cabedelo": [-6.9811, -34.8339], "casserengue": [-6.7214, -35.6836],
    "cuite": [-6.4853, -36.1550], "dona ines": [-6.6217, -35.6267], "fagundes": [-7.3756, -35.7761], "guarabira": [-6.8547, -35.4914],
    "gurinhem": [-7.1211, -35.4244], "ibiara": [-7.5256, -38.4117], "itaporanga": [-7.3044, -38.1503], "itatuba": [-7.4372, -35.5392],
    "jacarau": [-6.6111, -35.1278], "juazeirinho": [-7.0653, -36.5786], "lagoa": [-6.5656, -37.7558], "lastro": [-6.5406, -38.2869],
    "manaira": [-7.7011, -38.1539], "mulungu": [-6.9419, -35.4522], "nova olinda": [-7.4789, -38.0436], "picui": [-6.5103, -36.3456],
    "pirpirituba": [-6.7797, -35.4986], "pitimbu": [-7.4664, -34.8089], "pombal": [-6.7725, -37.8014], "queimadas": [-7.3592, -35.8972],
    "remigio": [-6.9297, -35.7925], "riachao do bacamarte": [-7.2536, -35.5975], "riacho dos cavalos": [-6.4422, -37.6492], "sao bento": [-6.4828, -37.4503],
    "sao francisco": [-6.8044, -38.0831], "sao joao do rio do peixe": [-6.7236, -38.4483], "sao joao do tigre": [-8.0811, -36.8506], "sao jose de princesa": [-7.7378, -38.0936],
    "sape": [-7.0964, -35.2319], "serra redonda": [-7.1856, -35.5911], "sossego": [-6.7644, -36.2514], "tacima": [-6.4883, -35.6372],
    "tenorio": [-6.9536, -36.6322], "umbuzeiro": [-7.6975, -35.5986], "vieiropolis": [-6.6433, -38.2436]
}

# --- FUNÇÃO AUXILIAR DE LIMPEZA DE ACENTOS ---
def limpar_texto_muni(txt):
    return str(txt).lower().strip().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("â","a").replace("ê","e").replace("ô","o").replace("ã","a").replace("õ","a").replace("ç","c")

# --- CARREGAMENTO IMPECÁVEL DE BANCOS DE DADOS ---
df_sec = pd.DataFrame()
if os.path.exists("secretarios_cosems_pb.csv"):
    for enc in ["utf-8-sig", "latin1", "cp1252"]:
        try:
            df_sec = pd.read_csv("secretarios_cosems_pb.csv", sep=";", dtype=str)
            df_sec.columns = df_sec.columns.str.strip()
            break
        except Exception: continue

df_pac = pd.DataFrame()
if os.path.exists("PB - Lima(PAC_PB).csv"):
    try: df_pac = pd.read_csv("PB - Lima(PAC_PB).csv", sep=";", encoding="utf-8-sig", dtype=str)
    except Exception: df_pac = pd.read_csv("PB - Lima(PAC_PB).csv", sep=";", encoding="latin1", dtype=str)
    df_pac.columns = df_pac.columns.str.strip()

df_ret = pd.DataFrame()
if os.path.exists("PB - Lima(RetomadaObras).csv"):
    try: df_ret = pd.read_csv("PB - Lima(RetomadaObras).csv", sep=";", encoding="utf-8-sig", dtype=str)
    except Exception: df_ret = pd.read_csv("PB - Lima(RetomadaObras).csv", sep=";", encoding="latin1", dtype=str)
    df_ret.columns = df_ret.columns.str.strip()

# --- 🎛️ PAINEL LATERAL TOTALMENTE REORGANIZADO ---
st.sidebar.header("Navegação do Sistema")
tipo_acompanhamento = st.sidebar.radio(
    "Selecione a ação desejada:",
    ["Obras Novo PAC", "Retomada de Obras Paralisadas", "🗺️ Georreferenciamento"]
)
st.sidebar.markdown("---")

obras_filtradas = pd.DataFrame()
muni, uf, prop_escolhida, msg_contexto, programa_nome = "", "PB", "", "", ""

# =========================================================================
# FLUXO 1: OBRAS NOVO PAC
# =========================================================================
if tipo_acompanhamento == "Obras Novo PAC":
    st.title("🏗️ Monitoramento Estratégico - Pendências de Obras no SISMOB")
    st.subheader("⚡ Painel de Controle — Novo PAC")
    
    if df_pac.empty:
        st.error("⚠️ Planilha do Novo PAC não carregada."); st.stop()
        
    for col in df_pac.columns: df_pac[col] = df_pac[col].fillna("").astype(str).str.strip()
    
    metodo_busca = st.sidebar.radio("Filtrar PAC por:", ["Município", "Proposta", "Prioridade de Contato"], key="busca_pac")

    if metodo_busca == "Município":
        busca_muni = st.text_input("Digite o nome do Município:", key="muni_pac")
        if busca_muni.strip():
            obras_filtradas = df_pac[df_pac["Município"].str.lower().str.contains(busca_muni.lower().strip(), na=False)]
    elif metodo_busca == "Proposta":
        busca_prop = st.text_input("Digite o número exato da Proposta:", key="prop_pac")
        if busca_prop.strip(): obras_filtradas = df_pac[df_pac["Proposta"] == busca_prop.strip()]
    elif metodo_busca == "Prioridade de Contato":
        lista_prioridades = sorted([p for p in df_pac["Prioridade de contato"].unique() if p != ""])
        busca_prio = st.selectbox("Selecione o nível de prioridade emergencial:", lista_prioridades, key="prio_pac_sel")
        if busca_prio: obras_filtradas = df_pac[df_pac["Prioridade de contato"] == busca_prio]

    if not obras_filtradas.empty:
        opcoes_obras = [f"{row['Proposta']} - {row.get('Nome da unidade', 'Obra')} ({row.get('Município', 'PB')})" for idx, row in obras_filtradas.iterrows()]
        obra_selecionada = st.selectbox("Selecione a obra do PAC para abrir os detalhes:", opcoes_obras, key="sel_pac")
        
        prop_escolhida = obra_selecionada.split(" - ").strip()
        dados_obra = obras_filtradas[obras_filtradas["Proposta"] == prop_escolhida].iloc
        
        muni = dados_obra.get("Município", "").upper()
        unidade = dados_obra.get("Nome da unidade", "")
        comp = dados_obra.get("Componente", "")
        sit_sismob = dados_obra.get("Situação no SISMOB", "")
        exec_fisica = dados_obra.get("Execução física (%) SISMOB", "")
        dias_sem_mon = dados_obra.get("Dias sem monitoramento SISMOB", "")
        prioridade = dados_obra.get("Prioridade de contato", "")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Proposta:** {prop_escolhida} | **UF:** PB")
            st.markdown(f"**Município:** {muni}")
            st.markdown(f"**Unidade:** {unidade}")
            st.markdown(f"**Componente:** {comp}")
        with col2:
            st.markdown(f"**Situação SISMOB:** {sit_sismob}")
            st.markdown(f"**Execução Física:** {exec_fisica}%")
            st.markdown(f"**Dias Sem Monit.:** {dias_sem_mon} dias")
            st.markdown(f"**Prioridade de Contato:** `{prioridade}`")

        msg_contexto = f"• Unidade: {unidade}\n• Componente: {comp}\n• Situação SISMOB: {sit_sismob}\n• Execução Física: {exec_fisica}%\n• Dias Sem Monitoramento: {dias_sem_mon}\n• Prioridade: {prioridade}"
        programa_nome = "Obras Novo PAC"
# =========================================================================
# FLUXO 2: RETOMADA DE OBRAS PARALISADAS
# =========================================================================
elif tipo_acompanhamento == "Retomada de Obras Paralisadas":
    st.title("🏗️ Monitoramento Estratégico - Pendências de Obras no SISMOB")
    st.subheader("🔄 Painel de Controle — Retomada de Obras")
    
    if df_ret.empty:
        st.error("⚠️ Planilha de Retomada não carregada."); st.stop()
        
    for col in df_ret.columns: df_ret[col] = df_ret[col].fillna("").astype(str).str.strip()

    metodo_busca = st.sidebar.radio("Filtrar Retomada por:", ["Município", "Proposta", "Prioridade de Contato"], key="busca_ret")

    if metodo_busca == "Município":
        busca_muni = st.text_input("Digite o nome do Município:", key="muni_ret")
        if busca_muni.strip():
            obras_filtradas = df_ret[df_ret["Município"].str.lower().str.contains(busca_muni.lower().strip(), na=False)]
    elif metodo_busca == "Proposta":
        busca_prop = st.text_input("Digite o número exato da Proposta:", key="prop_ret")
        if busca_prop.strip(): obras_filtradas = df_ret[df_ret["Proposta"] == busca_prop.strip()]
    elif metodo_busca == "Prioridade de Contato":
        lista_prioridades = sorted([p for p in df_ret["Prioridade de contato"].unique() if p != ""])
        busca_prio = st.selectbox("Selecione o nível de prioridade emergencial:", lista_prioridades, key="prio_ret_sel")
        if busca_prio: obras_filtradas = df_ret[df_ret["Prioridade de contato"] == busca_prio]

    if not obras_filtradas.empty:
        opcoes_obras = [f"{row['Proposta']} - {row.get('Nome da unidade', 'Obra')} ({row.get('Município', 'PB')})" for idx, row in obras_filtradas.iterrows()]
        obra_selecionada = st.selectbox("Selecione a obra para detalhar:", opcoes_obras, key="sel_ret")
        
        prop_escolhida = obra_selecionada.split(" - ").strip()
        dados_obra = obras_filtradas[obras_filtradas["Proposta"] == prop_escolhida].iloc
        
        muni = dados_obra.get("Município", "").upper()
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
            st.markdown(f"**Proposta:** {prop_escolhida} | **UF:** PB")
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
# FLUXO 3: NOVO SISTEMA DE GEORREFERENCIAMENTO INTEGRADO TRICOR
# =========================================================================
else:
    st.title("🗺️ Painel de Georreferenciamento das Transferências")
    st.subheader("Análise Territorial de Demandas de Infraestrutura em Saúde")
    
    modo_mapa = st.radio(
        "Selecione o filtro geográfico de mapa:",
        ["Apenas Obras Novo PAC", "Apenas Retomada de Obras Paralisadas", "🚨 Mapeamento Crítico (PAC e Retomada Simultâneos)"],
        horizontal=True
    )
    
    dados_mapa = []
    
    # LÓGICA 1: Apenas PAC
    if modo_mapa == "Apenas Obras Novo PAC" and not df_pac.empty:
        df_unicos = df_pac.drop_duplicates(subset=["Município"])
        for idx, row in df_unicos.iterrows():
            muni_l = limpar_texto_muni(row.get("Município", ""))
            if muni_l in coordenadas_pb:
                tot = len(df_pac[df_pac["Município"].str.lower().str.strip() == row.get("Município", "").lower().strip()])
                dados_mapa.append({"lat": float(coordenadas_pb[muni_l]), "lon": float(coordenadas_pb[muni_l]), "Município": row.get("Município", "").upper(), "Obras PAC": tot, "Obras Retomada": 0, "Total Geral": tot, "Status": "Apenas PAC"})
        st.success(f"📍 Mapeados {len(dados_mapa)} municípios com pendências exclusivas do Novo PAC.")

    # LÓGICA 2: Apenas Retomada
    elif modo_mapa == "Apenas Retomada de Obras Paralisadas" and not df_ret.empty:
        df_unicos = df_ret.drop_duplicates(subset=["Município"])
        for idx, row in df_unicos.iterrows():
            muni_l = limpar_texto_muni(row.get("Município", ""))
            if muni_l in coordenadas_pb:
                tot = len(df_ret[df_ret["Município"].str.lower().str.strip() == row.get("Município", "").lower().strip()])
                dados_mapa.append({"lat": float(coordenadas_pb[muni_l]), "lon": float(coordenadas_pb[muni_l]), "Município": row.get("Município", "").upper(), "Obras PAC": 0, "Obras Retomada": tot, "Total Geral": tot, "Status": "Apenas Retomada"})
        st.warning(f"📍 Mapeados {len(dados_mapa)} municípios com contratos de Retomada Paralisados.")

    # LÓGICA 3: Mapeamento Crítico (Simultâneos)
    elif not df_pac.empty and not df_ret.empty:
        muni_pac_set = set(df_pac["Município"].dropna().apply(limpar_texto_muni).unique())
        muni_ret_set = set(df_ret["Município"].dropna().apply(limpar_texto_muni).unique())
        
        muni_simultaneos = muni_pac_set.intersection(muni_ret_set)
        
        for m_limpo in muni_simultaneos:
            if m_limpo in coordenadas_pb:
                nome_real = df_pac[df_pac["Município"].apply(limpar_texto_muni) == m_limpo]["Município"].iloc.upper()
                tot_pac = len(df_pac[df_pac["Município"].apply(limpar_texto_muni) == m_limpo])
                tot_ret = len(df_ret[df_ret["Município"].apply(limpar_texto_muni) == m_limpo])
                
                dados_mapa.append({
                    "lat": float(coordenadas_pb[m_limpo]), "lon": float(coordenadas_pb[m_limpo]),
                    "Município": nome_real, "Obras PAC": tot_pac, "Obras Retomada": tot_ret,
                    "Total Geral": tot_pac + tot_ret, "Status": "🚨 ALERTA CRÍTICO: Possui Ambos os Programas"
                })
        st.error(f"🚨 ATENÇÃO: Identificados {len(dados_mapa)} MUNICÍPIOS CRÍTICOS com obras nos dois programas simultaneamente!")

    if dados_mapa:
        df_mapa = pd.DataFrame(dados_mapa)
        st.map(df_mapa, latitude="lat", longitude="lon", zoom=7)
        
        with st.expander("📊 Detalhamento Estatístico do Painel Geográfico"):
            st.dataframe(df_mapa[["Município", "Obras PAC", "Obras Retomada", "Total Geral", "Status"]].sort_values(by="Total Geral", ascending=False), use_container_width=True, index=False)

# =========================================================================
# BLOCO INTEGRADO: SECRETÁRIOS (COSEMS/PB) + WHATSAPP (MANTIDO SEGURO)
# =========================================================================
if not obras_filtradas.empty and muni:
    st.markdown("---")
    st.subheader("📋 Dados de Contato do Gestor Local")
    nome_secretario, fone_secretario = "Não localizado no cadastro", ""
    
    if not df_sec.empty:
        colunas_l = {c: c.strip().lower().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ã","a").replace("ç","c") for c in df_sec.columns}
        col_muni_sec = next((orig for orig, limpa in colunas_l.items() if "municip" in limpa), df_sec.columns)
        col_nome_sec = next((orig for orig, limpa in colunas_l.items() if "nome" in limpa or "secretario" in limpa or "gestor" in limpa), None)
        col_fone_sec = next((orig for orig, limpa in colunas_l.items() if "tel" in limpa or "cel" in limpa or "fone" in limpa or "whats" in limpa or "zap" in limpa), None)
        
        filtro_sec = df_sec[df_sec[col_muni_sec].str.lower().str.strip() == muni.lower().strip()]
        if not filtro_sec.empty:
            nome_secretario = filtro_sec.iloc[col_nome_sec] if col_nome_sec else "Não Informado"
            fone_secretario = filtro_sec.iloc[col_fone_sec] if col_fone_sec else ""

    st.write(f"**Secretário(a) de Saúde:** {nome_secretario}")
    st.write(f"**WhatsApp/Telefone:** {fone_secretario if fone_secretario else 'Não informado'}")

    saudacao = "Prezado(a) Secretário(a)" if "Não localizado" in nome_secretario else f"Prezado(a) Secretário(a) {nome_secretario}"
    mensagem_whatsapp = (
        f"{saudacao},\n\n"
        f"Entramos em contato para verificar a evolução técnica e pendências de engenharia em seu município, vinculadas ao programa de {programa_nome}:\n\n"
        f"📌 *DADOS DO INSTRUMENTO:*\n"
        f"• Município: {muni} - PB\n"
        f"• Proposta Nº: {prop_escolhida}\n"
        f"{msg_contexto}\n\n"
        f"Solicitamos atenção especial quanto ao andamento dos trâmites administrativos para a regularização do objeto. "
        f"Permanecemos à disposição para suporte técnico."
    )
    
    st.text_area("Visualização da Mensagem:", value=mensagem_whatsapp, height=200)
    
    if fone_secretario:
        num_limpo = "".join(filter(str.isdigit, fone_secretario))
        if len(num_limpo) <= 11 and num_limpo != "": num_limpo = f"55{num_limpo}"
        st.markdown(f"[📲 Enviar Diretamente via WhatsApp Web](https://whatsapp.com{num_limpo}&text={urllib.parse.quote(mensagem_whatsapp)})")
    
    st.code(mensagem_whatsapp, language="text")

# Rodapé Técnico do Corecon
st.markdown("---")
st.markdown("<p style='text-align:right; font-size:12px; color:gray;'>Bartolomeu Lima - Corecon-ES 1541</p>", unsafe_allow_html=True)
