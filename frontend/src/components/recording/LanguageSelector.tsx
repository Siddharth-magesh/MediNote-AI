"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Languages } from "lucide-react";
import { cn } from "@/lib/utils";

export interface Language {
  code: string;
  label: string;
  nativeLabel?: string;
}

export const SUPPORTED_LANGUAGES: Language[] = [
  { code: "en", label: "English", nativeLabel: "English" },
  { code: "hi", label: "Hindi", nativeLabel: "हिंदी" },
  { code: "ta", label: "Tamil", nativeLabel: "தமிழ்" },
  { code: "te", label: "Telugu", nativeLabel: "తెలుగు" },
  { code: "bn", label: "Bengali", nativeLabel: "বাংলা" },
  { code: "mr", label: "Marathi", nativeLabel: "मराठी" },
  { code: "gu", label: "Gujarati", nativeLabel: "ગુજરાતી" },
  { code: "kn", label: "Kannada", nativeLabel: "ಕನ್ನಡ" },
  { code: "ml", label: "Malayalam", nativeLabel: "മലയാളം" },
  { code: "pa", label: "Punjabi", nativeLabel: "ਪੰਜਾਬੀ" },
];

interface LanguageSelectorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  showIcon?: boolean;
  showNativeLabel?: boolean;
  className?: string;
}

export function LanguageSelector({
  value,
  onChange,
  disabled = false,
  showIcon = true,
  showNativeLabel = true,
  className,
}: LanguageSelectorProps) {
  const selectedLanguage = SUPPORTED_LANGUAGES.find((l) => l.code === value);

  return (
    <Select value={value} onValueChange={onChange} disabled={disabled}>
      <SelectTrigger className={cn("w-[160px]", className)}>
        {showIcon && <Languages className="mr-2 h-4 w-4 shrink-0" />}
        <SelectValue placeholder="Select language">
          {selectedLanguage?.label}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {SUPPORTED_LANGUAGES.map((lang) => (
          <SelectItem key={lang.code} value={lang.code}>
            <div className="flex items-center gap-2">
              <span>{lang.label}</span>
              {showNativeLabel && lang.nativeLabel !== lang.label && (
                <span className="text-muted-foreground text-xs">
                  ({lang.nativeLabel})
                </span>
              )}
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

// Compact language selector for inline use
interface LanguageChipSelectorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  className?: string;
}

export function LanguageChipSelector({
  value,
  onChange,
  disabled = false,
  className,
}: LanguageChipSelectorProps) {
  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {SUPPORTED_LANGUAGES.slice(0, 5).map((lang) => (
        <button
          key={lang.code}
          onClick={() => onChange(lang.code)}
          disabled={disabled}
          className={cn(
            "px-3 py-1.5 rounded-full text-sm font-medium transition-colors",
            "focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary",
            value === lang.code
              ? "bg-primary text-primary-foreground"
              : "bg-muted hover:bg-muted/80 text-muted-foreground",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
}
