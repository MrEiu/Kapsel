class Kapsel < Formula
  desc "Next-generation cross-platform terminal capsule & ergonomic shell multiplexer"
  homepage "https://github.com/MrEiu/Kapsel"
  version "0.2.1"
  license "MIT"

  on_macos do
    url "https://github.com/MrEiu/Kapsel/releases/download/v0.2.1/kapsel-macos-universal.tar.gz"
  end

  on_linux do
    url "https://github.com/MrEiu/Kapsel/releases/download/v0.2.1/kapsel-linux-x86_64.tar.gz"
  end

  def install
    bin.install "kapsel"
    bin.install "kps"
  end

  test do
    assert_match "Kapsel", shell_output("#{bin}/kapsel --version")
    assert_match "Kapsel", shell_output("#{bin}/kps --version")
  end
end
