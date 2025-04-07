<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![project_license][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">

<h3 align="center">Arnold Log Viewer</h3>

  <p align="center">
    Arnold Log Viewer is a lightweight tool for parsing, filtering, and visualizing Arnold renderer logs to streamline debugging and optimization. 
    <br />
    <a href="https://github.com/carlocarfora/arnold-log-viewer"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://carlocarfora-arnold-log-viewer-app-c0imqg.streamlit.app/">View Demo</a>
    &middot;
    <a href="https://github.com/carlocarfora/arnold-log-viewer/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/carlocarfora/arnold-log-viewer/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

Arnold Log Viewer is a lightweight and user-friendly application designed to help developers and artists analyze Arnold renderer logs efficiently. It provides a clean interface to parse, filter, and visualize log data, making debugging and performance optimization easier.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built With

[![Python][Python]][python-url]  
[![Streamlit][Streamlit]][streamlit-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

- Python

### Installation

1. Clone the repo:
    ```sh
    git clone https://github.com/carlocarfora/arnold-log-viewer.git
    ```
2. Install packages from `requirements.txt`
    ```sh
    pip install -r requirements.txt
    ```
3. Ensure streamlit runs with the following:
    ```sh
    streamlit hello
    ```
4. Run the app with the following
    ```sh
    streamlit run app.py
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Drop a text file of an Arnold log into the app or copy/paste an Arnold log into the text area.


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

Needed to have a working v1
- [x] finish framing all the functions to match the UI
- [x] finish definign all the functions to parse the log properly
- [ ] change camera in Render Info section
- [ ] change CPU/GPU in Render Info section
- [ ] hook up all functions to existing UI elements
- [ ] remove emojis in the headers as each part is done
- [ ] name entry point to name of app for side bar
- [ ] link the sidebar headings to the app
- [ ] make the warnings and errors display nicely

Nice to have once it's working
- [ ] format dahsboard with nicer colours
- [ ] add some more useful charts
- [ ] add a feature to export as an image

See the [open issues](https://github.com/carlocarfora/arnold-log-viewer/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/carlocarfora/arnold-log-viewer/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=carlocarfora/arnold-log-viewer" alt="contrib.rocks image" />
</a>


<!-- LICENSE -->
## License

Distributed under the project_license. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

[@carlo_carfora](https://twitter.com/carlo_carfora)

[https://github.com/carlocarfora/arnold-log-viewer](https://github.com/carlocarfora/arnold-log-viewer)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
<!--
## Acknowledgments
* []()
* []()
* []()
<p align="right">(<a href="#readme-top">back to top</a>)</p>
 -->


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/carlocarfora/arnold-log-viewer.svg?style=for-the-badge
[contributors-url]: https://github.com/carlocarfora/arnold-log-viewer/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/carlocarfora/arnold-log-viewer.svg?style=for-the-badge
[forks-url]: https://github.com/carlocarfora/arnold-log-viewer/network/members
[stars-shield]: https://img.shields.io/github/stars/carlocarfora/arnold-log-viewer.svg?style=for-the-badge
[stars-url]: https://github.com/carlocarfora/arnold-log-viewer/stargazers
[issues-shield]: https://img.shields.io/github/issues/carlocarfora/arnold-log-viewer.svg?style=for-the-badge
[issues-url]: https://github.com/carlocarfora/arnold-log-viewer/issues
[license-shield]: https://img.shields.io/github/license/carlocarfora/arnold-log-viewer.svg?style=for-the-badge
[license-url]: https://github.com/carlocarfora/arnold-log-viewer/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/carlocarfora
[Python]: https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff
[python-url]: https://www.python.org/
[Streamlit]: https://img.shields.io/badge/Streamlit-000?logo=streamlit&logoColor=fff
[streamlit-url]: https://streamlit.io/