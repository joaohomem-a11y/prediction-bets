interface LogoProps {
  size?: "sm" | "md" | "lg";
  showText?: boolean;
  className?: string;
}

const SIZES = {
  sm: 24,
  md: 28,
  lg: 40,
} as const;

function LogoIcon({ size }: { size: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      className="flex-shrink-0"
    >
      <defs>
        <linearGradient id="pb-grad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#2D7FF9" />
          <stop offset="100%" stopColor="#7B61FF" />
        </linearGradient>
      </defs>
      {/* Rounded square background */}
      <rect x="1" y="1" width="30" height="30" rx="8" fill="url(#pb-grad)" />
      {/* Signal pulse line */}
      <polyline
        points="6,22 11,18 15,20 20,11 25,14"
        stroke="#fff"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      {/* Peak dot */}
      <circle cx="20" cy="11" r="2.2" fill="#fff" />
    </svg>
  );
}

export default function Logo({ size = "md", showText = true, className = "" }: LogoProps) {
  const px = SIZES[size];

  if (!showText) {
    return <LogoIcon size={px} />;
  }

  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <LogoIcon size={px} />
      <span className="font-semibold tracking-tight select-none text-[length:inherit]">
        <span className="text-pb-text-primary">Prediction</span>
        <span className="text-pb-accent-blue">Bets</span>
      </span>
    </span>
  );
}
