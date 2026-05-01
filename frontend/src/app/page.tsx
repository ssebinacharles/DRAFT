import { redirect } from "next/navigation";

export default function Home() {
  // Automatically redirect users from the root "/" to your new dashboard
  redirect("/supervisor/assignments"); 
}