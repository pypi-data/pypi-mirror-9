import re

class SearchDirection:
    FORWARD = 1
    BACKWARD = -1

def findAll(document, search_text, line_interval=None, case_sensitive=True, word=False):
    """
    Find all occurrences of a given search text (evt. regexp text).
    """
    match_pos = []
    if line_interval is None:
        line_interval = (1, document.numLines()+1)
    else:
        line_interval = (max(1, line_interval[0]), min(document.numLines()+1, line_interval[1]))

    flags = 0
    if not case_sensitive:
       flags = re.IGNORECASE

    if word:
        search_text = r'\b'+re.escape(search_text)+r'\b'
    else:
        search_text = re.escape(search_text)

    allMatches = re.compile(search_text, flags).finditer

    for line_num in range(*line_interval):
        line_text = document.lineText(line_num)
        match_pos.extend( ((line_num, m.start()+1, m.end()+1) for m in allMatches(line_text)) )

    return match_pos

def find(buffer, text, direction):
    """
    Find the next occurrence of text in the buffer, with a given direction.
    If found, it moves the cursor to the appropriate position and returns True
    If not found, it returns false.
    """

    document = buffer.document
    cursor = buffer.cursor

    pos = cursor.pos

    current_line, current_col = pos

    # We do either forward or reverse search all with the same code.
    # We just switch the lookup function depending on the direction.
    # and apply it to each line string.
    if direction == SearchDirection.FORWARD:
        first_half, second_half = ((pos[0], document.numLines()+1), (1, pos[0]+1))
        find_routine = "find"
    else:
        first_half, second_half = ((pos[0], 0, -1), (document.numLines(), pos[0]-1, -1))
        find_routine = "rfind"


    # Perform the lookup in the first half.
    for line_num in range(*first_half):
        start, stop = (None, None)
        if line_num == current_line:
            # current_col - 1 + 1 = next char
            start, stop = (current_col, None) if direction == SearchDirection.FORWARD else (None, current_col)

        index = getattr(document.lineText(line_num), find_routine)(text, start, stop)
        if index != -1:
            cursor.toPos((line_num, index+1))
            return True

    # Reached the end, start from the other side
    for line_num in range(*second_half):
        start, stop = (None, None)
        if line_num == current_line:
            start, stop = (None, current_col) if direction == SearchDirection.FORWARD else (current_col, None)
        else:
            start, stop = (0, None)

        index = getattr(document.lineText(line_num), find_routine)(text, start, stop)

        if index != -1:
            cursor.toPos((line_num, index+1))
            return True

    return False

