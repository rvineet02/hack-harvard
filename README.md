# ASL-to-text

This project is a submission to HackHarvard 2022.

[DEVPOST](https://devpost.com/software/metaspeak)

# Models

Models are trained manually using a live 3D point cloud of your hands using mediapipe. We campture multiple points per second to achieve a large enough dataset to train our chosen model structure, PointNet.

## abc model

Trained model that recognizes every latter in the English alphabet (using Signs).

## conversation model

Trained model on the basics of ASL.

Words used:

-   yes
-   no
-   hello
-   bye
-   how
-   old
-   you
-   me
-   explore
-   deaf
-   good
-   bad
