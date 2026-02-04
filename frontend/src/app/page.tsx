import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Mic, FileText, Shield, Stethoscope, Languages, Clock } from "lucide-react";

interface FeatureCardProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
}

function FeatureCard({ icon: Icon, title, description }: FeatureCardProps) {
  return (
    <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
      <CardContent className="pt-6">
        <div className="flex flex-col items-center text-center space-y-4">
          <div className="p-3 bg-primary/10 rounded-full">
            <Icon className="h-8 w-8 text-primary" />
          </div>
          <h3 className="text-xl font-semibold">{title}</h3>
          <p className="text-muted-foreground">{description}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-primary/5 via-background to-background">
      {/* Navigation */}
      <nav className="container flex items-center justify-between py-6">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-primary rounded-lg">
            <Stethoscope className="h-6 w-6 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold">MediNote AI</span>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="ghost" asChild>
            <Link href="/login">Sign In</Link>
          </Button>
          <Button asChild>
            <Link href="/register">Get Started</Link>
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container py-24 text-center">
        <div className="max-w-3xl mx-auto space-y-6">
          <h1 className="text-5xl font-bold tracking-tight sm:text-6xl">
            Transform Consultations into{" "}
            <span className="text-primary">Smart Reports</span>
          </h1>
          <p className="text-xl text-muted-foreground">
            MediNote AI automatically transcribes doctor-patient conversations and
            generates structured prescriptions, diet plans, and care instructions
            using advanced AI.
          </p>
          <div className="flex gap-4 justify-center pt-4">
            <Button size="lg" asChild>
              <Link href="/register">
                Start Free Trial
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container py-24">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">Why Choose MediNote AI?</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Designed by healthcare professionals for healthcare professionals.
            Save time, reduce errors, and focus on what matters most - your patients.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <FeatureCard
            icon={Mic}
            title="Voice Recording"
            description="Record consultations with real-time transcription. Just speak naturally and let AI handle the rest."
          />
          <FeatureCard
            icon={FileText}
            title="Smart Reports"
            description="AI extracts prescriptions, diet plans, and care instructions automatically from your conversations."
          />
          <FeatureCard
            icon={Languages}
            title="Multi-Language"
            description="Support for 10+ Indian languages including Hindi, Tamil, Telugu, Bengali, and more."
          />
          <FeatureCard
            icon={Shield}
            title="Secure & Compliant"
            description="HIPAA-ready with encrypted storage, access controls, and audit trails for all patient data."
          />
          <FeatureCard
            icon={Clock}
            title="Save Time"
            description="Reduce documentation time by up to 70%. Generate complete reports in minutes, not hours."
          />
          <FeatureCard
            icon={Stethoscope}
            title="Medical Accuracy"
            description="AI trained on medical terminology ensures accurate extraction of symptoms, diagnoses, and treatments."
          />
        </div>
      </section>

      {/* How It Works Section */}
      <section className="container py-24 bg-muted/30 -mx-4 px-4 sm:mx-0 sm:px-0 sm:rounded-3xl">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">How It Works</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Three simple steps to transform your practice
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold mx-auto">
              1
            </div>
            <h3 className="text-xl font-semibold">Record</h3>
            <p className="text-muted-foreground">
              Select your patient and start recording the consultation in any supported language.
            </p>
          </div>
          <div className="text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold mx-auto">
              2
            </div>
            <h3 className="text-xl font-semibold">Review</h3>
            <p className="text-muted-foreground">
              AI extracts key information. Review and edit the generated prescription and care plan.
            </p>
          </div>
          <div className="text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold mx-auto">
              3
            </div>
            <h3 className="text-xl font-semibold">Share</h3>
            <p className="text-muted-foreground">
              Download or share the professional PDF report with your patient instantly.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container py-24 text-center">
        <div className="max-w-2xl mx-auto space-y-6">
          <h2 className="text-3xl font-bold">Ready to Transform Your Practice?</h2>
          <p className="text-muted-foreground">
            Join thousands of healthcare professionals who are saving time and
            improving patient care with MediNote AI.
          </p>
          <Button size="lg" asChild>
            <Link href="/register">Get Started Free</Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Stethoscope className="h-5 w-5 text-primary" />
            <span className="font-semibold">MediNote AI</span>
          </div>
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} MediNote AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
