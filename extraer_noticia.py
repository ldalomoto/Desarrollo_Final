from newspaper import Article
from experiments.test_prompt import noticia


def extract_news(url: str) -> str | None:
    """
    Extrae el texto completo de una noticia desde un link.
    NO usa IA.
    Funciona con la mayoría de diarios digitales.
    """
    try:
        article = Article(url, language="es")
        article.download()
        article.parse()

        text = article.text.strip()

        if len(text) < 100:
            return None

        return text

    except Exception as e:
        print(f"Error extrayendo noticia: {e}")
        return None


if __name__ == "__main__":
    url = input("Pega el link de la noticia:\n> ")

    text = extract_news(url)

    noticia(text)

    if text:
        print("\n✅ NOTICIA EXTRAÍDA:\n")
        print(text)
    else:
        print("\n❌ No se pudo extraer la noticia")
