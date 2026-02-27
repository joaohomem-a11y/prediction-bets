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
      {/* Head silhouette */}
      <ellipse cx="16" cy="13.5" rx="7" ry="7.5" fill="#fff" opacity="0.15" />
      {/* Hair / top of head */}
      <path d="M9.5 12c0-4 3-7 6.5-7s6.5 3 6.5 7" fill="#1a1a2e" />
      {/* Face */}
      <ellipse cx="16" cy="15" rx="6" ry="6.5" fill="#f0d5a8" />
      {/* Dark sunglasses */}
      <rect x="8.5" y="13" width="6" height="3.5" rx="1.2" fill="#1a1a2e" />
      <rect x="17.5" y="13" width="6" height="3.5" rx="1.2" fill="#1a1a2e" />
      {/* Glasses bridge */}
      <line x1="14.5" y1="14.5" x2="17.5" y2="14.5" stroke="#1a1a2e" strokeWidth="1" />
      {/* Glasses shine */}
      <line x1="9.5" y1="14" x2="11.5" y2="14" stroke="#fff" strokeWidth="0.6" strokeLinecap="round" opacity="0.5" />
      <line x1="18.5" y1="14" x2="20.5" y2="14" stroke="#fff" strokeWidth="0.6" strokeLinecap="round" opacity="0.5" />
      {/* Confident smirk */}
      <path d="M13.5 19.5c1 1 3.5 1 4.5 0" stroke="#c47a4a" strokeWidth="1" strokeLinecap="round" fill="none" />
      {/* Collar / suit hint */}
      <path d="M11 22l2.5-1.5h5L21 22" stroke="#fff" strokeWidth="0.8" strokeLinecap="round" fill="none" opacity="0.6" />
      <line x1="16" y1="20.5" x2="16" y2="23" stroke="#fff" strokeWidth="0.8" strokeLinecap="round" opacity="0.4" />
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
