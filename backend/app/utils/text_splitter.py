from typing import List, Dict, Any, Optional

# Split text into chunks
def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200, separator: str = '\n') -> List[str]:
    if not text:
        return []
    
    # Split text by separator
    segments = text.split(separator)
    chunks = []
    current_chunk = []
    current_size = 0
    
    for segment in segments:
        # If segment is too large, split it further
        if len(segment) > chunk_size:
            # If current chunk is not empty, add it first
            if current_size > 0:
                chunks.append(separator.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            # Split large segment
            sub_segments = split_long_segment(segment, chunk_size)
            chunks.extend(sub_segments)
            continue
        
        # If adding this segment would exceed chunk size, save current chunk first
        if current_size + len(segment) > chunk_size and current_size > 0:
            chunks.append(separator.join(current_chunk))
            
            # Keep some overlapping content
            overlap_size = min(current_size, chunk_overlap)
            overlap_items = current_chunk[-int(overlap_size / (current_size / len(current_chunk)) + 0.5):]
            
            current_chunk = overlap_items.copy()
            current_size = len(separator.join(current_chunk))
        
        current_chunk.append(segment)
        current_size += len(segment) + len(separator)
    
    # Add the last chunk
    if current_chunk:
        chunks.append(separator.join(current_chunk))
    
    return chunks

# Split overly long segments
def split_long_segment(segment: str, max_size: int) -> List[str]:
    chunks = []
    i = 0
    
    while i < len(segment):
        chunks.append(segment[i:i + max_size])
        i += max_size
    
    return chunks

