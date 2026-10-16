import java.util.List;

public class ComplexityDemo {

    // CC = 1 (no branches)
    public String greet(String name) {
        return "Hello, " + name;
    }

    // CC = 3 (if + ||)
    public boolean isEligibleForDiscount(int age, boolean isMember) {
        if (age < 12 || age > 65) {
            return true;
        }
        return isMember;
    }

    // CC = 7 (if, else if, if, if, &&, if)
    public double shippingCost(double weight, String country, boolean express) {
        double cost;
        if (weight <= 1) {
            cost = 5;
        } else if (weight <= 5) {
            cost = 10;
        } else {
            cost = 20;
        }
        if (!country.equals("FR")) {
            cost *= 2;
        }
        if (express && weight < 10) {
            cost += 15;
        }
        if (weight > 30) {
            cost += 50;
        }
        return cost;
    }

    // CC = 13 (too many branches: the "refactor me" example)
    public String processOrder(List<Double> prices, boolean isVip, String coupon, String country) {
        if (prices == null) return "invalid";
        if (prices.isEmpty()) return "empty";

        double total = 0;
        for (double p : prices) {
            if (p < 0) return "bad price";
            total += p;
        }

        if (isVip && total > 100) {
            total *= 0.9;
        } else if (coupon != null && coupon.equals("SAVE10")) {
            total -= 10;
        }

        switch (country) {
            case "FR": total *= 1.20; break;
            case "DE": total *= 1.19; break;
            case "ES": total *= 1.21; break;
        }

        return total > 1000 ? "manual review" : "ok";
    }

    // CC = 26 (the "scary" example: should trigger the highest warning level)
    public String classifyTransaction(double amount, String currency, String country,
                                      boolean isNewCustomer, int failedAttempts, String channel) {
        if (amount <= 0) return "invalid";
        if (currency == null || currency.isEmpty()) return "invalid";

        int risk = 0;

        if (amount > 10000) {
            risk += 3;
        } else if (amount > 1000) {
            risk += 2;
        } else if (amount > 100) {
            risk += 1;
        }

        if (isNewCustomer && amount > 500) {
            risk += 2;
        }

        if (failedAttempts > 3 || failedAttempts < 0) {
            risk += 3;
        }

        switch (country) {
            case "KP":
            case "IR":
                return "blocked";
            case "RU":
            case "NG":
                risk += 2;
                break;
            case "FR":
            case "DE":
                risk -= 1;
                break;
        }

        for (int i = 0; i < failedAttempts; i++) {
            if (i % 2 == 0 && risk < 10) {
                risk++;
            }
        }

        if (channel != null) {
            if (channel.equals("ATM")) {
                risk += 1;
            } else if (channel.equals("ONLINE") && isNewCustomer) {
                risk += 2;
            }
        }

        return risk >= 8 ? "reject" : risk >= 4 ? "review" : "approve";
    }
}