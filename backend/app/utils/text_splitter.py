from typing import List, Dict, Any, Optional

# 将文本分割成块
def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200, separator: str = '\n') -> List[str]:
    if not text:
        return []
    
    # 按分隔符分割文本
    segments = text.split(separator)
    chunks = []
    current_chunk = []
    current_size = 0
    
    for segment in segments:
        # 如果段落太大，进一步分割
        if len(segment) > chunk_size:
            # 如果当前块不为空，先添加它
            if current_size > 0:
                chunks.append(separator.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            # 分割大段落
            sub_segments = split_long_segment(segment, chunk_size)
            chunks.extend(sub_segments)
            continue
        
        # 如果添加这个段落会超出块大小，先保存当前块
        if current_size + len(segment) > chunk_size and current_size > 0:
            chunks.append(separator.join(current_chunk))
            
            # 保留一部分重叠内容
            overlap_size = min(current_size, chunk_overlap)
            overlap_items = current_chunk[-int(overlap_size / (current_size / len(current_chunk)) + 0.5):]
            
            current_chunk = overlap_items.copy()
            current_size = len(separator.join(current_chunk))
        
        current_chunk.append(segment)
        current_size += len(segment) + len(separator)
    
    # 添加最后一个块
    if current_chunk:
        chunks.append(separator.join(current_chunk))
    
    return chunks

# 分割过长的段落
def split_long_segment(segment: str, max_size: int) -> List[str]:
    chunks = []
    i = 0
    
    while i < len(segment):
        chunks.append(segment[i:i + max_size])
        i += max_size
    
    return chunks

