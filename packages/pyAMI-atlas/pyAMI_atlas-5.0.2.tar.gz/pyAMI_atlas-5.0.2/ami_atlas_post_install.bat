@echo off

SET mypath=%~dp0

%mypath%\..\python %mypath%\ami_atlas_post_install %*
