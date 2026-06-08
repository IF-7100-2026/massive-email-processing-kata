class ClasificadorPalabrasClave:
    """Clasificador de correos basado en coincidencia de palabras clave."""

    CATEGORIAS = {
        "Suscripcion": ["suscribirme", "boletin", "suscripcion", "suscripcion"],
        "Queja": ["queja", "reclamo", "molesto", "problema"],
        "Solicitud de informacion": ["informacion", "informacion", "consulta", "pregunta"],
        "Envio de noticia": ["noticia", "reportar", "denuncia", "suceso"]
    }

    CATEGORIA_DEFECTO = "Atencion humana"

    @classmethod
    def clasificar(cls, asunto: str, contenido: str) -> str:
        """Clasifica un correo segun su asunto y contenido usando palabras clave."""
        texto = f"{asunto} {contenido}".lower()

        for categoria, palabras in cls.CATEGORIAS.items():
            for palabra in palabras:
                if palabra in texto:
                    return categoria

        return cls.CATEGORIA_DEFECTO