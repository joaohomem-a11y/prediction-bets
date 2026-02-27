interface LogoProps {
  size?: "sm" | "md" | "lg";
  showText?: boolean;
  className?: string;
}

const SIZES = {
  sm: 24,
  md: 32,
  lg: 48,
} as const;

function LogoIcon({ size }: { size: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      className="flex-shrink-0"
    >
      <defs>
        <linearGradient id="pb-ball" x1="8" y1="6" x2="32" y2="34" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#2D7FF9" />
          <stop offset="100%" stopColor="#7B61FF" />
        </linearGradient>
        <radialGradient id="pb-glow" cx="50%" cy="40%" r="50%">
          <stop offset="0%" stopColor="#fff" stopOpacity="0.18" />
          <stop offset="100%" stopColor="#fff" stopOpacity="0" />
        </radialGradient>
      </defs>
      {/* Ball */}
      <circle cx="20" cy="17" r="13" stroke="url(#pb-ball)" strokeWidth="2.5" fill="none" />
      <circle cx="20" cy="17" r="13" fill="url(#pb-glow)" />
      {/* Lightning bolt */}
      <path d="M22 8L16 18h5l-3 11 8-13h-5.5L22 8z" fill="#F5A623" />
      {/* Base */}
      <path
        d="M12 31c0-1 1.5-2.5 8-2.5s8 1.5 8 2.5"
        stroke="url(#pb-ball)"
        strokeWidth="2.2"
        strokeLinecap="round"
        fill="none"
      />
      <line x1="10" y1="34" x2="30" y2="34" stroke="url(#pb-ball)" strokeWidth="2.2" strokeLinecap="round" />
    </svg>
  );
}

export default function Logo({ size = "md", showText = true, className = "" }: LogoProps) {
  const px = SIZES[size];

  if (!showText) {
    return <LogoIcon size={px} />;
  }

  return (
    <span className={`inline-flex items-center gap-1.5 ${className}`}>
      <LogoIcon size={px} />
      <span className="font-extrabold italic tracking-tight select-none">
        <span className="text-pb-text-primary">PREDICTION</span>
        <span className="text-pb-accent-blue">BETS</span>
      </span>
    </span>
  );
}
