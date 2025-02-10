## **Objetivo**  
Desenvolver um script em Python que recebe como entrada um arquivo no formato Markdown (`.md`) contendo texto em português brasileiro e gera um arquivo de áudio (`.mp3` ou outro formato adequado) como saída, utilizando tecnologia de síntese de voz (TTS - Text-to-Speech).  

## **Requisitos Funcionais**  
1. O script deve ler um arquivo Markdown fornecido como entrada.  
2. Deve converter o texto do Markdown para fala (TTS), preservando a estrutura do texto para uma leitura natural.  
3. A saída do áudio deve ser gerada em um formato comum, como `.mp3` ou `.wav`.  
4. O idioma do texto e da fala deve ser exclusivamente o português brasileiro.  
5. Deve suportar caracteres especiais e acentos da língua portuguesa.  
6. O usuário deve poder configurar a velocidade da fala e a escolha da voz, caso aplicável.  
7. O script deve permitir a execução via linha de comando, recebendo o caminho do arquivo Markdown como argumento.  

## **Requisitos Não Funcionais**  
1. O código deve seguir as boas práticas de desenvolvimento em Python, incluindo:  
   - Organização modular  
   - Nomes de variáveis e funções descritivos  
   - Documentação clara  
   - Tratamento de erros adequado  
2. O processamento deve ser eficiente, suportando arquivos Markdown de tamanho moderado (~100 páginas).  
3. O código deve ser compatível com Python 3.8+ e seguir as diretrizes PEP8.  
4. Deve ser utilizado um motor de TTS de alta qualidade, como Google Text-to-Speech (`gTTS`), `pyttsx3`, `edge-tts`, ou outro que ofereça boa naturalidade na leitura.  

## **Especificações Técnicas**  
1. **Entrada:**  
   - Um arquivo `.md` contendo o texto formatado em Markdown.  
   - O usuário pode fornecer parâmetros opcionais, como velocidade da fala e voz.  
   
2. **Processamento:**  
   - O script deve converter o Markdown em texto puro, removendo formatações desnecessárias.  
   - Deve interpretar corretamente títulos, listas, parágrafos e blocos de código.  
   - O texto processado será enviado para o mecanismo de TTS selecionado.  

3. **Saída:**  
   - Um arquivo de áudio (`.mp3` ou `.wav`) salvo no mesmo diretório do arquivo de entrada, com o mesmo nome base.  

## **Exemplo de Uso**  
Execução via terminal:  
```bash
python markdown_to_audio.py entrada.md --output output.mp3 --speed 1.2 --voice "default"
```
Onde:  
- `entrada.md`: Arquivo de entrada  
- `--output output.mp3`: Nome do arquivo de saída (opcional, padrão: mesmo nome do `.md`)  
- `--speed 1.2`: Ajuste da velocidade da fala (opcional)  
- `--voice "default"`: Escolha da voz (opcional)  

## **Tratamento de Erros**  
- Arquivo Markdown não encontrado → Exibir mensagem de erro e abortar.  
- Formato do arquivo inválido → Notificar o usuário.  
- Problemas com o serviço TTS → Exibir mensagem amigável e sugerir solução.  

## **Sugestões de Bibliotecas**  
- `markdown` para processamento do texto Markdown  
- `gTTS`, `pyttsx3` ou `edge-tts` para conversão de texto em fala  
- `argparse` para tratamento de argumentos de linha de comando  

## **Critérios de Aceitação**  
- O script deve converter corretamente arquivos Markdown em áudio.  
- O áudio gerado deve ser claro e inteligível em português brasileiro.  
- O tempo de execução deve ser razoável para arquivos médios (~100 páginas).  
- O código deve ser bem estruturado e documentado.  

====

Segue abaixo uma implementação em Python que atende aos requisitos especificados. O script utiliza as bibliotecas:

- **markdown** para converter o Markdown em HTML;
- **BeautifulSoup** (do pacote `bs4`) para extrair o texto puro do HTML;
- **pyttsx3** para a conversão de texto em fala, permitindo ajustar a velocidade e escolher a voz;
- **pydub** (opcional) para converter o áudio gerado em WAV para MP3, caso o usuário deseje.

> **Observação:**  
> - Caso o usuário opte por gerar um arquivo MP3 e a biblioteca `pydub` não estiver instalada (ou o ffmpeg não estiver disponível no sistema), o script exibirá uma mensagem de erro.  
> - No Ubuntu, o motor padrão do `pyttsx3` é o *espeak*, que pode ter qualidade inferior se comparado a outros motores. Se houver vozes em português instaladas no sistema, o script tentará selecionar uma delas quando a opção de voz for deixada como “default”.  
> - Instale as dependências necessárias (se ainda não estiverem instaladas) com:  
> 
> ```bash
> pip install markdown beautifulsoup4 pyttsx3 pydub
> ```  
> 
> Certifique-se também de que o *ffmpeg* esteja instalado para que a conversão para MP3 funcione.

```python
#!/usr/bin/env python3
import argparse
import os
import sys
import markdown
from bs4 import BeautifulSoup
import pyttsx3

# Tenta importar o pydub para conversão de áudio (WAV -> MP3)
try:
    from pydub import AudioSegment
    PDUB_AVAILABLE = True
except ImportError:
    PDUB_AVAILABLE = False


def markdown_to_text(input_file):
    """
    Lê o arquivo Markdown, converte para HTML e extrai o texto puro.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            md_content = f.read()
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo: {e}")
    # Converte Markdown para HTML
    html = markdown.markdown(md_content)
    # Extrai texto do HTML
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n")
    return text


def configure_tts_engine(engine, speed, voice_name):
    """
    Configura o motor TTS:
      - Ajusta a velocidade da fala;
      - Seleciona a voz desejada.
      
    Se a opção de voz for "default", tenta escolher uma voz que contenha "português" ou "pt" no nome.
    """
    # Ajusta a velocidade (rate)
    rate = engine.getProperty("rate")
    engine.setProperty("rate", int(rate * speed))

    voices = engine.getProperty("voices")
    if voice_name.lower() == "default":
        # Tenta selecionar uma voz em português, se disponível
        for v in voices:
            if "português" in v.name.lower() or "pt" in v.name.lower():
                engine.setProperty("voice", v.id)
                break
    else:
        found = False
        for v in voices:
            if voice_name.lower() in v.name.lower():
                engine.setProperty("voice", v.id)
                found = True
                break
        if not found:
            print(f"Voz '{voice_name}' não encontrada. Utilizando voz padrão.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Converte um arquivo Markdown para áudio utilizando TTS."
    )
    parser.add_argument("input", help="Caminho do arquivo Markdown (.md) de entrada")
    parser.add_argument(
        "--output",
        help="Nome do arquivo de áudio de saída (.mp3 ou .wav). "
             "Caso não seja informado, utiliza o mesmo nome base do .md e extensão .wav",
        default=None,
    )
    parser.add_argument(
        "--speed",
        type=float,
        help="Velocidade da fala (ex.: 1.0 para normal, 1.2 para 20%% mais rápido). Padrão: 1.0",
        default=1.0,
    )
    parser.add_argument(
        "--voice",
        help="Nome da voz a ser utilizada (padrão: 'default').",
        default="default",
    )
    args = parser.parse_args()

    # Verifica existência e formato do arquivo de entrada
    if not os.path.isfile(args.input):
        print("Arquivo Markdown não encontrado.", file=sys.stderr)
        sys.exit(1)
    if not args.input.lower().endswith(".md"):
        print("Formato inválido: utilize um arquivo com extensão .md", file=sys.stderr)
        sys.exit(1)

    try:
        text = markdown_to_text(args.input)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print("O arquivo Markdown está vazio ou não contém texto válido.", file=sys.stderr)
        sys.exit(1)

    # Define o nome do arquivo de saída
    if args.output is None:
        base = os.path.splitext(args.input)[0]
        output_file = base + ".wav"  # padrão: WAV
    else:
        output_file = args.output

    # Inicializa o motor TTS
    try:
        engine = pyttsx3.init()
    except Exception as e:
        print(f"Erro ao inicializar o motor TTS: {e}", file=sys.stderr)
        sys.exit(1)

    configure_tts_engine(engine, args.speed, args.voice)

    # Se o usuário deseja MP3, gera inicialmente um arquivo WAV temporário
    temp_wav = output_file
    need_conversion = False
    if output_file.lower().endswith(".mp3"):
        temp_wav = "temp_audio.wav"
        need_conversion = True

    # Gera o áudio a partir do texto
    try:
        engine.save_to_file(text, temp_wav)
        engine.runAndWait()
    except Exception as e:
        print(f"Erro durante a conversão TTS: {e}", file=sys.stderr)
        sys.exit(1)

    # Se for solicitado MP3, converte o arquivo WAV gerado
    if need_conversion:
        if not PDUB_AVAILABLE:
            print(
                "Conversão para MP3 solicitada, mas a biblioteca 'pydub' não está instalada."
                " Instale-a ou escolha saída em .wav.",
                file=sys.stderr,
            )
            sys.exit(1)
        try:
            audio = AudioSegment.from_wav(temp_wav)
            audio.export(output_file, format="mp3")
            os.remove(temp_wav)
        except Exception as e:
            print(f"Erro na conversão de WAV para MP3: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"Arquivo de áudio gerado: {output_file}")
    else:
        print(f"Arquivo de áudio gerado: {temp_wav}")


if __name__ == "__main__":
    main()
```