import { Component, type ErrorInfo, type ReactNode } from "react";

export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("GARDA rendering error", error.name, info.componentStack);
  }
  render() {
    if (this.state.failed) {
      return <main className="login" role="alert">
        <h1>GARDA</h1><p>Tampilan mengalami gangguan. Data tersimpan tidak dihapus.</p>
        <button className="primary" onClick={() => this.setState({ failed: false })}>Coba kembali</button>
      </main>;
    }
    return this.props.children;
  }
}
