{ pkgs }: {
  deps = [
    pkgs.bfg-repo-cleaner
    pkgs.gdb
    pkgs.replitPackages.prybar-python310
    pkgs.replitPackages.stderred
  ];
}