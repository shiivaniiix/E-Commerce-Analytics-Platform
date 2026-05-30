function ErrorAlert({ message }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <p className="text-red-800">{message}</p>
    </div>
  );
}

export default ErrorAlert;
