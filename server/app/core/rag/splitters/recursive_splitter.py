from langchain_text_splitters import RecursiveCharacterTextSplitter

def create_recursive_splitter(
) -> RecursiveCharacterTextSplitter:
    """
    递归字符文档切分器
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=128,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter