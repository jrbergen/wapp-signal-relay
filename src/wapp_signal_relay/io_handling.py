from copy import copy
from pathlib import Path
import re


DUPLICATE_TGT_PATH_REX = re.compile(r'(.+)_\(\d+\)$')


def get_nonexisting_target_path(initial_tgt: Path) -> Path:

    new_tgt_path = copy(initial_tgt)

    if initial_tgt.exists():
        dupe_num = 1

        initial_suffix = initial_tgt.suffix

        while new_tgt_path.exists():

            new_fname = DUPLICATE_TGT_PATH_REX.sub(repl=f"\1_({dupe_num}){initial_suffix}",
                                                   string=new_tgt_path.with_suffix('').name)
            new_tgt_path = initial_tgt.parent / new_fname
            dupe_num += 1
    return new_tgt_path




