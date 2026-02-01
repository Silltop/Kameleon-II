export function LoginModal() {
  const handleLogin = () => {
    window.location.href = '/login'
  }

  return (
    <dialog id="login-modal" className="modal">
      <div className="modal-box">
        <h3 className="font-bold text-lg mb-4">Sign in to your account</h3>
        <p className="py-4">
          Click the button below to sign in with your credentials.
        </p>
        <div className="modal-action">
          <button onClick={handleLogin} className="btn btn-primary btn-block">
            Log in with OAuth
          </button>
        </div>
      </div>
      <form method="dialog" className="modal-backdrop">
        <button>close</button>
      </form>
    </dialog>
  )
}
