import { getRequestConfig } from "next-intl/server";
import { routing } from "./routing";

type Locale = (typeof routing.locales)[number];

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  if (!locale || !routing.locales.includes(locale as Locale)) {
    locale = routing.defaultLocale;
  }

  const messages = await (async () => {
    switch (locale) {
      case "pt":
        return (await import("../../messages/pt.json")).default;
      case "es":
        return (await import("../../messages/es.json")).default;
      default:
        return (await import("../../messages/en.json")).default;
    }
  })();

  return {
    locale,
    messages,
  };
});
