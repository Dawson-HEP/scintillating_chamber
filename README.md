<style>
p:has(+ ul) {
  margin-bottom: 0;
}
p + ul {
  margin-top: 0;
}
</style>

# [Dawson HEP](https://youtu.be/Yp-H1ZBjPuM)

Introduction Video:

[![Demo video](https://img.youtube.com/vi/Yp-H1ZBjPuM/maxresdefault.jpg)](https://youtu.be/Yp-H1ZBjPuM)


## About us

![Icons](https://skillicons.dev/icons?i=python,htmx,gtk,latex)


**The Dawson High Energy Physics** club, run by Dr. Manuel Toharia Zapata is a place for curious college students to learn more about particle physics. Every week, students from a wide variety of programs meet to learn and discuss about flavour physisc, extra dimensions and much more. We engage with both theory and experiments, learning about and observing particles. Our many projects include an Alpha particle detector, spark chamber, Scintillating Chamber, and more.

Here's a [video](https://youtu.be/Yp-H1ZBjPuM) about our group!

![Scintillating chamber](.//docs/figures/big%20detector.jpg)

Our proposal to the 2025 [Beamline for schools](https://beamlineforschools.cern/) competition. It consists of an arrangement of scitillator rods to detect and model the trajectory of cosmic ray in three dimensions. The possible trajectories are then calculated and displayed graphically to the user.

**See Paper [HERE](./proposal/proposal.pdf)**

## How to install and run display
1) install python requirements with ```pip install -r requirements.txt```
   - note that for windows, installing imgui[glfw] can be done in two ways:
     - installing Visual Studio C++ Build Tools >= 14.0 and then the requirements.txt after
     - utilising the provided wheel, with the command ```py -3.11 -m pip install wheels/imgui-2.0.0-cp311-cp311-win_amd64.whl```, if using python 3.11
   - subsequently, run ```pip install -r requirements.txt``` to get the other needed modules
2) install the program with ```pip install -e .```
3) run ```chamber -h``` to determine the desired run option




## Contacts

- Milo Belarbi
- David Birnbaum
- Tykhon Byshkin
- Matvey Chirchikov
- Danah Dézémé
- Arij Mohamedi
- [Evan Parasol](https://github.com/TheBookwyrms), blackdragon6493@gmail.com
- [Leandro Perez-Moran](https://github.com/LudioRex), pemle2007@gmail.com
- Ari Polterovich
- [Tian Yi, Xia](https://github.com/ThatAquarel), xtxiatianyi@gmail.com
- [Andy Yu](https://github.com/Anodymous1), andy.yu@dawsoncollege.qc.ca
- [Aljoscha Ziegler](https://github.com/Questionning), ziegleraljoscha@gmail.com
