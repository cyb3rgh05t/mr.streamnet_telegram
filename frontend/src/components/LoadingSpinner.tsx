import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner } from "@fortawesome/free-solid-svg-icons";

interface LoadingSpinnerProps {
  message?: string;
}

export default function LoadingSpinner({
  message = "Loading...",
}: LoadingSpinnerProps) {
  return (
    <div className="loading-container">
      <FontAwesomeIcon icon={faSpinner} className="spinner-icon" />
      <p className="loading-message">{message}</p>
    </div>
  );
}
