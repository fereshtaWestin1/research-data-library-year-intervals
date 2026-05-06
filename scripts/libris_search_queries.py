from matplotlib import Path


file_path =Path( "../../data/tidsperioder/alfabetisk_ordning_nordiska_Filtered_Temporal_TermsCHATGPT.txt")

def readfile():
    formatted_lines = []
    result = ""

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            if line:
                formatted_line = f'ÄMNE:"{line}"'
                formatted_lines.append(formatted_line)

    result = " OR ".join(formatted_lines)
    return result


def format_search():
    amne_items = readfile().split(" OR ")
    chunk_size = 35

    chunks = []
    current_chunk = []
    formatted_chunks = []

    for item in amne_items:
        current_chunk.append(item)
        if len(current_chunk) == chunk_size:
            chunks.append(' OR '.join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(' OR '.join(current_chunk))
    
    for idx, chunk in enumerate(chunks, 1):
        formatted_chunks.append(f"Chunk {idx}:\n({chunk}) AND BIB:Litteraturbanken\n")
    
    return formatted_chunks


def save():
    
    with open("libris_searchstrings.txt", "w", encoding="utf-8") as output:
        output.write('\n'.join(format_search()))


save()