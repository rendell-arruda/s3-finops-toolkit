def get_optimization_status(size_mb, lifecycle):
    if size_mb == 0.0:
        return "Bucket vazio", "Avaliar se pode ser deletado"
    elif lifecycle == "Sim":
        return "✅ Lifecycle configurado", "Nenhuma ação necessária"

    else:
        return "⚠️ Candidato a revisão", "Configurar lifecycle policy"
