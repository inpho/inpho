#!/bin/sh
echo "mining corpus"
python inpho/corpus/sep.py --all --occur

echo "processing Idea-Thinker graph edges"
python inpho/corpus/sep.py --all --entropy

echo "processing Idea-Idea graph edges"
python inpho/corpus/sep.py --idea

echo "processing Thinker-Thinker graph edges"
python inpho/corpus/sep.py --thinker

exit 0
