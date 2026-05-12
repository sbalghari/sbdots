# Maintainer: Saifullah Balghari

pkgname=sbdots-git
pkgver=r0.unknown
pkgrel=1
pkgdesc="Personal Hyprland dotfiles and environment management toolkit"
arch=('x86_64')
url="https://github.com/sbalghari/sbdots"
license=('MIT')

depends=(
  kitty
  ark
  firefox
  mission-center
  visual-studio-code-bin
  nautilus
  nautilus-code
  nautilus-copy-path
  nautilus-hide
  smile
  atuin
  blueman
  bluez-utils
  brightnessctl
  btop
  cava
  aur-check-updates
  pacman-contrib
  eza
  fastfetch
  figlet
  python-requests
  fish
  htop
  neofetch
  neovim
  network-manager-applet
  wlogout
  zram-generator
  pavucontrol
  power-profiles-daemon
  rofi
  reflector
  udiskie
  uwsm
  sddm
  waybar
  waypaper
  starship
  swaync
  swww
  noto-fonts
  ttf-dejavu
  ttf-firacode-nerd
  ttf-font-awesome
  ttf-intone-nerd
  ttf-jetbrains-mono
  ttf-jetbrains-mono-nerd
  ttf-liberation
  ttf-nerd-fonts-symbols
  ttf-nerd-fonts-symbols-mono
  ttf-roboto
  hypridle
  hyprland
  hyprland-protocols
  hyprlock
  hyprpicker
  hyprpolkitagent
  hyprshade
  hyprshot
  xdg-desktop-portal-hyprland
  gnome-text-editor
  loupe
  python-pywal
  tela-circle-icon-theme-standard
  bibata-cursor-theme-bin
  qt5-wayland
  qt5ct
  qt6-wayland
  qt6ct
  python
)

makedepends=(
  git
  python-build
  python-installer
  python-wheel
  python-setuptools
)

optdepends=(
  'sddm: display manager support'
  'hyprland: Wayland compositor'
)

source=(
  "git+https://github.com/sbalghari/sbdots.git#branch=feat/sbdotsctl"
)

sha256sums=('SKIP')

pkgver() {
  cd "$srcdir/sbdots"

  printf "r%s.%s" \
    "$(git rev-list --count HEAD)" \
    "$(git rev-parse --short HEAD)"
}

build() {
  cd "$srcdir/sbdots"

  python -m build --wheel --no-isolation
}

package() {
  cd "$srcdir/sbdots"

  python -m installer \
    --destdir="$pkgdir" \
    dist/*.whl

  # Install dotfiles backup
  install -dm755 "$pkgdir/usr/share/sbdots"

  cp -r dotfiles/* \
    "$pkgdir/usr/share/sbdots/"
}