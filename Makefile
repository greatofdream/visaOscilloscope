.PHONY: all

pathprefix:=./
runNo:=032 
# 030 031 
# 023 024 025 026 027 028 029
# 008 010 011 012 013 014 015
# 016 017 018 019 020 021 022
chs:= 3 4
N:=40000
sample: $(runNo:%=$(pathprefix)/data/run%.h5) 
ana: $(runNo:%=$(pathprefix)/data/res%.h5)
plot: $(runNo:%=$(pathprefix)/figure/%.png)
upload: $(runNo:%=$(pathprefix)/%.upload)
record: oscilloscopePython.md
	scp $^ greatofdream@10.160.28.69:/srv/greatofdream/JinpingPMTTest/pmtTest/
$(pathprefix)/data/run%.h5:
	date
	python sample.py -i $(chs) -o $@ -N $(N)
	date
$(pathprefix)/data/res%.h5: $(pathprefix)/data/run%.h5
	python analyze.py -i $^ -o $@ -c $(chs)
$(pathprefix)/figure/%.png: $(pathprefix)/data/res%.h5
	python plot.py -i $^ -o $@ -c $(chs)
$(pathprefix)/%.upload: $(pathprefix)/data/run%.h5
	scp $^ greatofdream@10.160.28.69:/mnt/neutrino/pmtTest/Ex2/
.SECONDARY:
.DELETE_ON_ERROR: